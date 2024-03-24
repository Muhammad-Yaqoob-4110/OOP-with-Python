from datetime import datetime
from collections import defaultdict

# Define the BookingException class
class BookingException(Exception):
    pass

# Define the Customer class
class Customer:
    def __init__(self, passportNumber, name, dob, contact):
        self._passportNumber = passportNumber
        self._name = name
        self._dob = dob
        self._contact = contact
    
    @property
    def passportNumber(self):
        return self._passportNumber
    
    @property
    def name(self):
        return self._name
    
    @property
    def contact(self):
        return self._contact
    
    def getAge(self):
        today = datetime.today()
        age = today.year - self._dob.year - ((today.month, today.day) < (self._dob.month, self._dob.day))
        return age
    
    def __str__(self):
        return f"Passport: {self._passportNumber} Name: {self._name} Age: {self.getAge()} Contact: {self._contact}"

# Define the Tour class
class Tour:
    def __init__(self, code, name, days, nights, cost):
        self._code = code
        self._name = name
        self._days = days
        self._nights = nights
        self._cost = cost
    
    @property
    def code(self):
        return self._code
    
    @property
    def name(self):
        return self._name
    
    @property
    def cost(self):
        return self._cost
    
    def getDaysNights(self):
        return f"{self._days}D/{self._nights}N"
    
    def __str__(self):
        return f"Tour Code: {self._code} Name: {self._name} ({self.getDaysNights()}) Base Cost: ${self._cost:.2f}"

# Define the ScheduledTour class
class ScheduledTour:
    handling_fee = 120
    
    def __init__(self, scheduleCode, tour, departureDateTime, lang, capacity, peak):
        self._scheduleCode = scheduleCode
        self._tour = tour
        self._departureDateTime = departureDateTime
        self._lang = lang
        self._capacity = capacity
        self._seatsAvailable = capacity
        self._status = True if peak else False
    
    @property
    def departureDateTime(self):
        return self._departureDateTime
    
    @property
    def capacity(self):
        return self._capacity
    
    @property
    def seatsAvailable(self):
        return self._seatsAvailable
    
    @property
    def status(self):
        return "Yes" if self._status else "No"
    
    def getAge(self):
        today = datetime.today()
        age = today.year - self._dob.year - ((today.month, today.day) < (self._dob.month, self._dob.day))
        return age
    
    def code(self):
        return f"{self._tour.code}-{self._scheduleCode}"
    
    def cost(self):
        return self._tour.cost
    
    def bookSeats(self, quantity):
        if self._seatsAvailable >= quantity:
            self._seatsAvailable -= quantity
            return True
        return False
    
    def cancelSeats(self, quantity):
        if self._seatsAvailable + quantity <= self._capacity:
            self._seatsAvailable += quantity
            return True
        return False
    
    def getPenaltyRate(self, cancellationDate):
        days_difference = (self._departureDateTime - cancellationDate).days
        if days_difference >= 46:
            return 0.1
        elif 45 >= days_difference >= 15:
            return 0.25
        elif 14 >= days_difference >= 8:
            return 0.5
        elif 7 >= days_difference > 0:
            return 1.0
        else:
            return 1.0
    
    def __str__(self):
        return f"Name: {self._tour.name} ({self._tour.getDaysNights()}) Base Cost: ${self._tour.cost:.2f}\n" \
               f"Code: {self.code()} Departure: {self._departureDateTime.strftime('%d-%b-%Y %H:%M')} " \
               f"Language: {self._lang}\n" \
               f"Capacity: {self._capacity} Available: {self._seatsAvailable} Open: {self.status}"

# Define the PeakScheduledTour class
class PeakScheduledTour(ScheduledTour):
    surcharge = 0.15
    handling_charges = 200
    
    def cost(self):
        return self._tour.cost * (1 + self.surcharge)
    
    def getPenaltyRate(self, cancellationDate):
        penalty_rate = super().getPenaltyRate(cancellationDate)
        return min(penalty_rate + 0.1, 1.0)

# Define the Booking class
class Booking:
    _NEXT_ID = 1
    
    def __init__(self, scheduledTour, customers):
        self._bookingId = Booking._NEXT_ID
        self._scheduledTour = scheduledTour
        self._customers = customers
        Booking._NEXT_ID += 1
    
    @property
    def bookingId(self):
        return self._bookingId
    
    @property
    def scheduledTour(self):
        return self._scheduledTour
    
    @property
    def customers(self):
        return self._customers
    
    @property
    def seats(self):
        return len(self._customers)
    
    def cost(self):
        return self._scheduledTour.cost() * self.seats
    
    def addSeats(self, customers):
        raise NotImplementedError
    
    def __str__(self):
        customer_info = "\n".join(str(customer) for customer in self._customers)
        return f"Booking Id: {self._bookingId} Seats: {self.seats} Final Cost: ${self.cost():.2f}\n" \
               f"{self._scheduledTour}\n" \
               f"{customer_info}"

# Define the IndividualBooking class
class IndividualBooking(Booking):
    _SINGLE = 0.5
    
    def __init__(self, scheduledTour, customer, single=False):
        super().__init__(scheduledTour, [customer])
        self._single = single
    
    def cost(self):
        base_cost = self._scheduledTour.cost()
        if self._single:
            return base_cost * (1 + self._SINGLE)
        return base_cost
    
    def __str__(self):
        return super().__str__()

# Define the GroupBooking class
class GroupBooking(Booking):
    _DISCOUNT = {6: 0.05, 10: 0.1}
    
    def __init__(self, scheduledTour, customers):
        super().__init__(scheduledTour, customers)
    
    def getDiscount(self):
        group_size = len(self._customers)
        for size, discount in sorted(self._DISCOUNT.items(), reverse=True):
            if group_size >= size:
                return discount
    def cost(self):
        base_cost = self._scheduledTour.cost()
        discount = self.getDiscount()
        if discount:
            return base_cost * (1 - discount)
        return base_cost * len(self._customers)
    
    def addSeats(self, customers):
        raise BookingException("Group booking cannot add more seats")
    
    def __str__(self):
        return super().__str__()

# Define the TourAgency class
class TourAgency:
    def __init__(self):
        self.customers = []  # list of customers
        self.tours = []  # list of tours
        self.scheduled_tours = defaultdict(list)  # dictionary with scheduled tour code as key and list of scheduled tours as value
        self.bookings = []  # list of bookings
    
    # Search methods
    def searchCustomer(self, passportNumber):
        for customer in self.customers:
            if customer.passportNumber == passportNumber:
                return customer
        return None
    
    def searchTour(self, tourCode):
        for tour in self.tours:
            if tour.code == tourCode:
                return tour
        return None
    
    def searchScheduledTour(self, scheduleCode):
        for scheduled_tour_list in self.scheduled_tours.values():
            for scheduled_tour in scheduled_tour_list:
                if scheduled_tour.code() == scheduleCode:
                    return scheduled_tour
        return None
    
    def searchBooking(self, bookingId):
        for booking in self.bookings:
            if booking.bookingId == bookingId:
                return booking
        return None
    
    # List methods
    def listTours(self):
        return "\n".join(str(tour) for tour in self.tours)
    
    def listScheduledTours(self):
        scheduled_tours = []
        for scheduled_tour_list in self.scheduled_tours.values():
            for scheduled_tour in scheduled_tour_list:
                scheduled_tours.append(str(scheduled_tour))
        return "\n".join(scheduled_tours)
    
    def listOpenScheduledTours(self):
        open_scheduled_tours = []
        for scheduled_tour_list in self.scheduled_tours.values():
            for scheduled_tour in scheduled_tour_list:
                if scheduled_tour.status == "Yes":
                    open_scheduled_tours.append(str(scheduled_tour))
        return "\n".join(open_scheduled_tours)

# Main function
def main():
    # Creating TourAgency object
    tour_agency = TourAgency()
    
    # Adding customers
    customer1 = Customer("E2000444N", "John Doe", datetime(1990, 5, 20), "1234567890")
    customer2 = Customer("EC4744643", "Jane Smith", datetime(1985, 9, 15), "9876543210")
    tour_agency.customers.extend([customer1, customer2])
    
    # Adding tours
    tour1 = Tour("JPHA08", "Best of Hokkaido", 8, 7, 2699.08)
    tour2 = Tour("KMBK08", "Mukbang Korea", 8, 6, 1699.36)
    tour3 = Tour("VNDA06", "Discover Vietnam", 6, 5, 999.00)
    tour_agency.tours.extend([tour1, tour2, tour3])
    
    # Adding scheduled tours
    scheduled_tour1 = ScheduledTour("505", tour1, datetime(2024, 5, 5, 10, 30), "English", 30, True)
    scheduled_tour2 = ScheduledTour("408", tour1, datetime(2024, 4, 8, 8, 45), "English", 25, False)
    scheduled_tour3 = ScheduledTour("503", tour2, datetime(2024, 5, 3, 8, 5), "English", 32, True)
    scheduled_tour4 = ScheduledTour("403", tour2, datetime(2024, 4, 3, 10, 5), "Mandarin", 25, False)
    scheduled_tour5 = ScheduledTour("503", tour3, datetime(2024, 5, 3, 11, 8), "Mandarin", 28, True)
    tour_agency.scheduled_tours[tour1.code].extend([scheduled_tour1, scheduled_tour2])
    tour_agency.scheduled_tours[tour2.code].extend([scheduled_tour3, scheduled_tour4])
    tour_agency.scheduled_tours[tour3.code].append(scheduled_tour5)
    
    # Menu loop
    while True:
        print("<<<< Main Menu >>>>")
        print("1. Tour management")
        print("2. Booking management")
        print("0. Quit")
        choice = input("Enter choice: ")
        
        if choice == "1":
            tour_management_menu(tour_agency)
        elif choice == "2":
            booking_management_menu(tour_agency)
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

# Tour management menu function
def tour_management_menu(tour_agency):
    while True:
        print("\n<< Tour Menu >>")
        print("1. Schedule Tour")
        print("2. Open/Close Scheduled Tour")
        print("3. Remove Scheduled Tour")
        print("4. List Scheduled Tours")
        print("0. Back to main menu")
        choice = input("Enter choice: ")
        
        if choice == "1":
            schedule_tour(tour_agency)
        elif choice == "2":
            open_close_scheduled_tour(tour_agency)
        elif choice == "3":
            remove_scheduled_tour(tour_agency)
        elif choice == "4":
            list_scheduled_tours(tour_agency)
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please try again.")

# Booking management menu function
def booking_management_menu(tour_agency):
    while True:
        print("\n<< Booking Menu >>")
        print("1. Create Booking")
        print("2. Cancel Booking")
        print("3. Add Seats to Booking")
        print("4. List Bookings")
        print("0. Back to main menu")
        choice = input("Enter choice: ")
        
        if choice == "1":
            create_booking(tour_agency)
        elif choice == "2":
            cancel_booking(tour_agency)
        elif choice == "3":
            add_seats_to_booking(tour_agency)
        elif choice == "4":
            list_bookings(tour_agency)
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please try again.")

# Function to schedule a tour
def schedule_tour(tour_agency):
    print("\n<< Schedule Tour >>")
    tour_code = input("Enter Tour Code: ")
    tour = tour_agency.searchTour(tour_code)
    if not tour:
        print("Tour not found.")
        return
    
    print("Available scheduled tours:")
    print(tour_agency.listScheduledTours())
    schedule_code = input("Enter Schedule Code: ")
    departure_date = input("Enter Departure Date and Time (YYYY-MM-DD HH:MM): ")
    lang = input("Enter Language: ")
    capacity = int(input("Enter Capacity: "))
    peak = input("Is it Peak (Yes/No): ").lower() == "yes"
    
    try:
        departure_datetime = datetime.strptime(departure_date, "%Y-%m-%d %H:%M")
    except ValueError:
        print("Invalid date and time format. Please enter in YYYY-MM-DD HH:MM format.")
        return
    
    scheduled_tour = ScheduledTour(schedule_code, tour, departure_datetime, lang, capacity, peak)
    tour_agency.scheduled_tours[tour_code].append(scheduled_tour)
    print("Scheduled tour added successfully.")

# Function to open/close scheduled tour
def open_close_scheduled_tour(tour_agency):
    print("\n<< Open/Close Scheduled Tour >>")
    schedule_code = input("Enter Scheduled Tour Code: ")
    scheduled_tour = tour_agency.searchScheduledTour(schedule_code)
    if not scheduled_tour:
        print("Scheduled tour not found.")
        return
    
    if scheduled_tour.status == "Yes":
        action = input("This scheduled tour is currently open. Do you want to close it? (Yes/No): ")
        if action.lower() == "yes":
            scheduled_tour._status = False
            print("Scheduled tour closed successfully.")
    else:
        action = input("This scheduled tour is currently closed. Do you want to open it? (Yes/No): ")
        if action.lower() == "yes":
            scheduled_tour._status = True
            print("Scheduled tour opened successfully.")

# Function to remove a scheduled tour
def remove_scheduled_tour(tour_agency):
    print("\n<< Remove Scheduled Tour >>")
    schedule_code = input("Enter Scheduled Tour Code to remove: ")
    scheduled_tour = tour_agency.searchScheduledTour(schedule_code)
    if not scheduled_tour:
        print("Scheduled tour not found.")
        return
    
    print(scheduled_tour)
    confirmation = input("Are you sure you want to remove this scheduled tour? (Yes/No): ")
    if confirmation.lower() == "yes":
        if scheduled_tour.seatsAvailable == scheduled_tour.capacity:
            del tour_agency.scheduled_tours[scheduled_tour._tour.code][schedule_code]
            print("Scheduled tour removed successfully.")
        else:
            print("Cannot remove scheduled tour. Some seats are already booked.")
    else:
        print("Operation cancelled.")

# Function to list all scheduled tours
def list_scheduled_tours(tour_agency):
    print("\n<< List Scheduled Tours >>")
    print(tour_agency.listScheduledTours())

# Function to create a booking
def create_booking(tour_agency):
    print("\n<< Create Booking >>")
    passport_number = input("Enter Passport Number: ")
    customer = tour_agency.searchCustomer(passport_number)
    if not customer:
        print("Customer not found.")
        return
    
    print("List of open scheduled tours:")
    print(tour_agency.listOpenScheduledTours())
    schedule_code = input("Enter Scheduled Tour Code: ")
    scheduled_tour = tour_agency.searchScheduledTour(schedule_code)
    if not scheduled_tour:
        print("Scheduled tour not found.")
        return
    
    booking_type = input("Enter Booking Type (I for Individual, G for Group): ").upper()
    if booking_type == "I":
        single = input("Is Single Room required? (Yes/No): ").lower() == "yes"
        booking = IndividualBooking(scheduled_tour, customer, single)
    elif booking_type == "G":
        customers = [customer]
        while True:
            passport_number = input("Enter Passport Number (<enter> to stop): ")
            if not passport_number:
                break
            customer = tour_agency.searchCustomer(passport_number)
            if not customer:
                print("Customer not found.")
                continue
            customers.append(customer)
        booking = GroupBooking(scheduled_tour, customers)
    else:
        print("Invalid booking type.")
        return
    
    tour_agency.bookings.append(booking)
    print("Booking created successfully.")

# Function to cancel a booking
def cancel_booking(tour_agency):
    print("\n<< Cancel Booking >>")
    booking_id = int(input("Enter Booking Id: "))
    booking = tour_agency.searchBooking(booking_id)
    if not booking:
        print("Booking not found.")
        return
    
    print(booking)
    cancellation_date = datetime.today()
    penalty_rate = booking.scheduledTour.getPenaltyRate(cancellation_date)
    penalty_amount = min(penalty_rate * booking.cost(), booking.cost())
    print(f"Penalty Amount: ${penalty_amount:.2f}")
    confirmation = input("Are you sure you want to cancel this booking? (Yes/No): ")
    if confirmation.lower() == "yes":
        tour_agency.bookings.remove(booking)
        booking.scheduledTour.cancelSeats(booking.seats)
        print("Booking cancelled successfully.")
    else:
        print("Operation cancelled.")

# Function to add seats to a booking
def add_seats_to_booking(tour_agency):
    print("\n<< Add Seats to Booking >>")
    booking_id = int(input("Enter Booking Id: "))
    booking = tour_agency.searchBooking(booking_id)
    if not booking:
        print("Booking not found.")
        return
    
    if isinstance(booking, IndividualBooking):
        print("Individual booking cannot add more travelers.")
        return
    
    print("List of customers already booked:")
    print("\n".join(str(customer) for customer in booking.customers))
    passport_numbers = []
    while True:
        passport_number = input("Enter Passport Number (<enter> to stop): ")
        if not passport_number:
            break
        customer = tour_agency.searchCustomer(passport_number)
        if not customer:
            print("Customer not found.")
            continue
        if customer in booking.customers:
            print("Customer already booked.")
            continue
        passport_numbers.append(passport_number)
    
    customers = [booking.scheduledTour.searchCustomer(passport_number) for passport_number in passport_numbers]
    if not all(customers):
        print("Some customers not found.")
        return
    
    if not booking.scheduledTour.bookSeats(len(customers)):
        print("No available seats for additional customers.")
        return
    
    booking.customers.extend(customers)
    print("Seats added to booking successfully.")
    additional_cost = booking.scheduledTour.cost() * len(customers)
    print(f"Additional Cost: ${additional_cost:.2f}")

# Function to list all bookings
def list_bookings(tour_agency):
    print("\n<< List Bookings >>")
    if not tour_agency.bookings:
        print("No bookings found.")
        return
    print("\n".join(str(booking) for booking in tour_agency.bookings))

if __name__ == "__main__":
    main()

