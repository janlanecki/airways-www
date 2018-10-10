"""Views for the website"""
from datetime import datetime

from django.contrib import auth
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum, Q
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseNotAllowed, HttpResponseBadRequest, JsonResponse, \
    HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from rest_framework import generics, permissions, mixins

from website.forms import SearchForm, TicketForm, SignupForm
from website.models import Flight, Ticket, Plane, Captain
from website.serializers import FlightSerializer, CaptainSerializer


def home(request):
    """Renders home page."""
    return render(request, 'base.html', locals())


def search(request):
    """Renders page with search results"""
    if not request.method == 'GET':
        return HttpResponseNotAllowed(['GET'])

    params = request.GET
    flights = Flight.objects.all()

    if params.get('day_from', '') == '' and params.get('day_to', '') == '':
        flights = flights.filter(day_from=datetime.now().date(), day_to=datetime.now().date())

    if params.get('airport_from', '') != '':
        flights = flights.filter(airport_from=params['airport_from'])
    if params.get('airport_to', '') != '':
        flights = flights.filter(airport_to=params['airport_to'])
    if params.get('day_from', '') != '':
        flights = flights.filter(day_from__gte=datetime.strptime(params['day_from'], '%Y-%m-%d'))
    if params.get('day_to', '') != '':
        flights = flights.filter(day_to__lte=datetime.strptime(params['day_to'], '%Y-%m-%d'))

    flights = flights.values()
    search_form = SearchForm(initial={
        'airport_from': params.get('airport_from', ''),
        'airport_to': params.get('airport_to', ''),
        'day_from': params.get('day_from', ''),
        'day_to': params.get('day_to', '')
    })

    return render(request, 'search.html',
                  {'request': request, 'flights': flights, 'search_form': search_form})


def details(request):
    """Renders page with flight details"""
    param = request.GET
    if not param.__contains__('id'):
        raise Http404

    flight = Flight.objects.filter(id=param['id'])
    if not flight.exists():
        raise Http404

    plane_id = flight.get().plane_id
    seats = Plane.objects.get(id=plane_id).seats

    flight = flight.get()
    captain_first_name = flight.captain.first_name
    captain_last_name = flight.captain.last_name

    tickets = Ticket.objects.filter(flight=flight.id).all()
    taken = tickets.aggregate(Sum('seats'))['seats__sum']
    free_seats = seats
    if taken is not None:
        free_seats -= taken

    if request.user.is_authenticated and flight.day_from >= datetime.now().date():
        if request.method == 'POST':
            ticket_form = TicketForm(request.POST)

            if ticket_form.is_valid():
                with transaction.atomic():
                    Flight.objects.select_for_update().filter(id=param['id'])
                    ticket = ticket_form.save(commit=False)
                    free_seats_after_purchase = free_seats - ticket.seats

                    if free_seats_after_purchase >= 0 and ticket.seats > 0:
                        ticket.user = request.user
                        ticket.flight = flight
                        ticket.save()
                        free_seats = free_seats_after_purchase
                    else:
                        bad_ticket = True
        else:
            ticket_form = TicketForm()

    if request.GET.__contains__('redirect'):
        link = request.GET.get('redirect')

    return render(request, 'details.html', locals())


def signup(request):
    """Renders sign up page"""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'],
                                            password=form.cleaned_data['password'])
            auth.login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'signup.html', locals())


@require_POST
def login(request):
    """Renders login page and logs in user"""
    user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        auth.login(request, user)
        return redirect(request.GET['redirect'])
    return redirect('search')


def logout(request):
    """Renders logout page and logs out user"""
    auth.logout(request)
    return redirect('home')


class FlightsAPIList(generics.ListAPIView):
    """Day's flights"""
    queryset = None
    serializer_class = FlightSerializer

    def get_queryset(self):
        date = self.kwargs.get('day')
        if date is not None:
            begin_date = datetime.strptime(date, '%Y-%m-%d')

            return Flight.objects.filter(day_from__exact=begin_date).\
                order_by('time_from').select_related()
        return Flight.objects.none()


class FlightAPIDetails(generics.RetrieveAPIView):
    """Flights information"""
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer


class ModifyCrewAPI(generics.GenericAPIView, mixins.UpdateModelMixin):
    """updating crew for flight"""
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (permissions.IsAuthenticated, )

    @staticmethod
    def post(request):
        """changes or adds crew assigned to flight if possible"""
        flight_id = request.POST.get('flight_id')
        captain_id = request.POST.get('captain_id')
        if not flight_id or not captain_id:
            return HttpResponseBadRequest()

        with transaction.atomic():
            flight = Flight.objects.filter(id=flight_id).get()
            captain = Captain.objects.filter(id=captain_id).select_for_update().get()
            available = captains_available(flight_id)

            if flight and captain and captain in available:
                serializer = FlightSerializer()
                serializer.update(flight, validated_data={'captain': captain_id})
                return JsonResponse({'id': captain_id, 'first_name': getattr(captain, 'first_name'),
                                     'last_name': getattr(captain, 'last_name')})

            return HttpResponseBadRequest()


def captains_available(flight_id):
    """gives set of captains available for the flight"""
    if flight_id:
        flight = Flight.objects.get(id=flight_id)
        fset = Flight.objects.filter(
            Q(day_from__exact=flight.day_from) &
            (Q(time_from__gte=flight.time_from, time_from__lt=flight.time_to) |
             Q(time_to__lte=flight.time_to, time_to__gt=flight.time_from) |
             Q(time_from__lte=flight.time_from, time_to__gte=flight.time_to)))

        return Captain.objects.exclude(id__in=fset.values_list('captain__id', flat=True))

    return Captain.objects.none()


class CrewAPIList(generics.ListAPIView):
    """Available crews"""
    serializer_class = CaptainSerializer

    def get_queryset(self):
        """returns available crews for the flight"""
        idx = self.kwargs.get('id')
        if idx:
            return captains_available(idx)
        return Captain.objects.none()


def captains_available_serialized(flight_id):
    """gives set of captains available for the flight in form {id: {first name, last name}}"""
    captains = captains_available(flight_id)
    result = {}
    for c in captains:
        result[c.id] = {"first_name": c.first_name, "last_name": c.last_name}
    return result


def server_data(request):
    """Gives all flights with available captains"""
    result = {}
    # TODO del filter
    flights = Flight.objects.filter(day_from__gte=datetime.strptime('2018-06-01', '%Y-%m-%d'), day_from__lt=datetime.strptime('2018-06-03', '%Y-%m-%d')).order_by('day_from', 'time_from', 'time_to')
    prev_day = flights[0].day_from
    flights_of_day = {}
    captains = {}
    if flights is not None:
        for f in flights:
            if f.day_from != prev_day:
                result[str(prev_day)] = flights_of_day
                flights_of_day = {}
                prev_day = f.day_from

            flights_of_day[str(f.id)] = FlightSerializer(f).data
            captains[f.id] = captains_available_serialized(f.id)

        result[str(prev_day)] = flights_of_day

    return JsonResponse({"flights": result, "captains": captains})


@require_POST
def modify_data(request):
    if request.user.is_authenticated:
        flights_list = []
        captains_list = []
        for i, j in request.POST.items():
            flights_list.append(i)
            captains_list.append(j)

        with transaction.atomic():
            Captain.objects.filter(id__in=captains_list).select_for_update()
            for i in range(0, len(captains_list)):
                captain = Captain.objects.get(id=captains_list[i])
                flight = Flight.objects.get(id=flights_list[i])
                available_captains = captains_available(flights_list[i])
                if captain in available_captains:
                    flight.captain = captain
                    flight.save()

        return HttpResponse(status=200)
    return HttpResponseForbidden()