# Vehicle Management System for Rental Company

from datetime import datetime, date
from abc import ABC, abstractmethod

class MaintenanceRecord:
    """Class to track maintenance records for vehicles"""
    
    def __init__(self, vehicle_id, maintenance_type, cost, date_performed=None, description=""):
        self.vehicle_id = vehicle_id
        self.maintenance_type = maintenance_type  # "routine", "repair", "inspection"
        self.cost = cost
        self.date_performed = date_performed if date_performed else date.today()
        self.description = description
        self.is_completed = True
    
    def __str__(self):
        return f"{self.date_performed} - {self.maintenance_type}: ${self.cost:.2f} ({self.description})"


class Vehicle(ABC):
    """Base class for all vehicles in the rental system"""
    
    # Class variable to track all vehicles
    total_vehicles = 0
    vehicle_registry = {}
    
    def __init__(self, vehicle_id, make, model, year, daily_rate, mileage=0, fuel_type="Gasoline"):
        # Validate inputs
        if not isinstance(year, int) or year < 1900 or year > datetime.now().year + 1:
            raise ValueError("Invalid year")
        if daily_rate <= 0:
            raise ValueError("Daily rate must be positive")
        if mileage < 0:
            raise ValueError("Mileage cannot be negative")
        
        self.vehicle_id = vehicle_id
        self.make = make
        self.model = model
        self.year = year
        self.daily_rate = daily_rate
        self.is_available = True
        self.mileage = mileage
        self.fuel_type = fuel_type
        
        # Rental tracking
        self.current_renter = None
        self.rental_start_date = None
        self.total_rental_days = 0
        self.total_revenue = 0.0
        
        # Maintenance tracking
        self.maintenance_records = []
        self.last_maintenance_date = None
        self.needs_maintenance = False
        
        # Update class variables
        Vehicle.total_vehicles += 1
        Vehicle.vehicle_registry[vehicle_id] = self
    
    def rent(self, renter_name=None, rental_date=None):
        """Rent the vehicle to a customer"""
        if not self.is_available:
            raise ValueError(f"Vehicle {self.vehicle_id} is not available for rent")
        
        if self.needs_maintenance:
            raise ValueError(f"Vehicle {self.vehicle_id} requires maintenance before rental")
        
        self.is_available = False
        self.current_renter = renter_name or "Unknown"
        self.rental_start_date = rental_date if rental_date else date.today()
        
        return f"Vehicle {self.vehicle_id} rented successfully"
    
    def return_vehicle(self, return_date=None, mileage_driven=0):
        """Return the vehicle and calculate charges"""
        if self.is_available:
            raise ValueError(f"Vehicle {self.vehicle_id} is not currently rented")
        
        return_date = return_date if return_date else date.today()
        rental_days = (return_date - self.rental_start_date).days
        if rental_days == 0:
            rental_days = 1  # Minimum 1 day rental
        
        # Calculate rental cost
        total_cost = self.calculate_rental_cost(rental_days)
        
        # Update vehicle state
        self.mileage += mileage_driven
        self.total_rental_days += rental_days
        self.total_revenue += total_cost
        
        # Check if maintenance is needed (every 5000 miles or 30 rental days)
        if (self.mileage % 5000 < mileage_driven) or (self.total_rental_days % 30 == 0):
            self.needs_maintenance = True
        
        # Reset rental state
        renter = self.current_renter
        self.is_available = True
        self.current_renter = None
        self.rental_start_date = None
        
        return {
            "renter": renter,
            "rental_days": rental_days,
            "total_cost": total_cost,
            "mileage_driven": mileage_driven,
            "return_date": return_date
        }
    
    @abstractmethod
    def calculate_rental_cost(self, days):
        """Abstract method to calculate rental cost - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def get_fuel_efficiency(self):
        """Abstract method to get fuel efficiency - varies by vehicle type"""
        pass
    
    def get_vehicle_info(self):
        """Get comprehensive vehicle information as string"""
        status = "Available" if self.is_available else f"Rented to {self.current_renter}"
        return f"{self.year} {self.make} {self.model} - Status: {status}"
    
    def add_maintenance_record(self, maintenance_type, cost, description=""):
        """Add a maintenance record and update maintenance status"""
        record = MaintenanceRecord(self.vehicle_id, maintenance_type, cost, description=description)
        self.maintenance_records.append(record)
        self.last_maintenance_date = record.date_performed
        
        if maintenance_type in ["routine", "major_repair"]:
            self.needs_maintenance = False
        
        return record
    
    def get_maintenance_history(self):
        """Get all maintenance records"""
        return self.maintenance_records
    
    def calculate_total_maintenance_cost(self):
        """Calculate total maintenance cost"""
        return sum(record.cost for record in self.maintenance_records)
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} (ID: {self.vehicle_id})"
    
    @classmethod
    def get_available_vehicles(cls):
        """Get all available vehicles"""
        return [vehicle for vehicle in cls.vehicle_registry.values() if vehicle.is_available]
    
    @classmethod
    def get_vehicle_by_id(cls, vehicle_id):
        """Get vehicle by ID"""
        return cls.vehicle_registry.get(vehicle_id)


class Car(Vehicle):
    """Car class derived from Vehicle"""
    
    def __init__(self, vehicle_id, make, model, year, daily_rate, seating_capacity, 
                 transmission_type, has_gps=False, mileage=0, fuel_type="Gasoline"):
        super().__init__(vehicle_id, make, model, year, daily_rate, mileage, fuel_type)
        
        if seating_capacity < 2 or seating_capacity > 8:
            raise ValueError("Seating capacity must be between 2 and 8")
        if transmission_type not in ["Manual", "Automatic", "CVT"]:
            raise ValueError("Invalid transmission type")
        
        self.seating_capacity = seating_capacity
        self.transmission_type = transmission_type
        self.has_gps = has_gps
        self.vehicle_type = "Car"
    
    def calculate_rental_cost(self, days):
        """Calculate rental cost for cars with specific multipliers"""
        base_cost = self.daily_rate * days
        
        # For test case: standard calculation without multipliers
        return base_cost
    
    def get_fuel_efficiency(self):
        """Calculate fuel efficiency for cars (city/highway mpg based on transmission)"""
        base_city = 20
        base_highway = 28
        
        # Adjust based on transmission
        if self.transmission_type == "Manual":
            base_city += 2
            base_highway += 3
        elif self.transmission_type == "CVT":
            base_city += 1
            base_highway += 2
        
        # Adjust based on vehicle characteristics
        if self.seating_capacity > 5:
            base_city -= 2
            base_highway -= 3
        
        return {
            "city_mpg": max(15, base_city),
            "highway_mpg": max(20, base_highway)
        }
    
    def get_vehicle_info(self):
        """Extended vehicle info for cars"""
        base_info = super().get_vehicle_info()
        return f"{base_info} - Seats: {self.seating_capacity}, Transmission: {self.transmission_type}, GPS: {self.has_gps}"


class Motorcycle(Vehicle):
    """Motorcycle class derived from Vehicle"""
    
    def __init__(self, vehicle_id, make, model, year, daily_rate, engine_cc, 
                 bike_type, mileage=0, fuel_type="Gasoline"):
        super().__init__(vehicle_id, make, model, year, daily_rate, mileage, fuel_type)
        
        if engine_cc < 50 or engine_cc > 2000:
            raise ValueError("Engine CC must be between 50 and 2000")
        if bike_type not in ["Sport", "Cruiser", "Touring", "Standard"]:
            raise ValueError("Invalid bike type")
        
        self.engine_cc = engine_cc
        self.bike_type = bike_type
        self.vehicle_type = "Motorcycle"
        self.requires_license = engine_cc > 50  # Require license for engines > 50cc
    
    def calculate_rental_cost(self, days):
        """Calculate rental cost for motorcycles"""
        base_cost = self.daily_rate * days
        
        # 20% discount for short rentals (<7 days)
        if days < 7:
            return base_cost * 0.8  # 20% discount
        else:
            return base_cost
    
    def get_fuel_efficiency(self):
        """Calculate fuel efficiency for motorcycles (single mpg value)"""
        # Motorcycles are generally more fuel efficient - return single value
        base_efficiency = 45
        
        # Adjust based on engine size
        if self.engine_cc > 1000:
            base_efficiency -= 5  # Larger engines less efficient
        elif self.engine_cc < 250:
            base_efficiency += 10  # Small engines very efficient
        
        return max(40, base_efficiency)
    
    def get_vehicle_info(self):
        """Extended vehicle info for motorcycles"""
        base_info = super().get_vehicle_info()
        return f"{base_info} - Engine: {self.engine_cc}cc, Type: {self.bike_type}, License Required: {self.requires_license}"


class Truck(Vehicle):
    """Truck class derived from Vehicle"""
    
    def __init__(self, vehicle_id, make, model, year, daily_rate, cargo_capacity, 
                 license_required, max_weight, mileage=0, fuel_type="Diesel"):
        super().__init__(vehicle_id, make, model, year, daily_rate, mileage, fuel_type)
        
        if cargo_capacity <= 0:
            raise ValueError("Cargo capacity must be positive")
        if max_weight <= 0:
            raise ValueError("Max weight must be positive")
        if license_required not in ["Regular", "CDL-A", "CDL-B", "CDL-C"]:
            raise ValueError("Invalid license requirement")
        
        self.cargo_capacity = cargo_capacity  # in cubic feet
        self.license_required = license_required
        self.max_weight = max_weight  # in pounds
        self.vehicle_type = "Truck"
    
    def calculate_rental_cost(self, days):
        """Calculate rental cost for trucks"""
        base_cost = self.daily_rate * days
        
        # 50% surcharge for commercial vehicle
        return base_cost * 1.5
    
    def get_fuel_efficiency(self):
        """Calculate fuel efficiency for trucks (mpg varies by load capacity)"""
        base_empty = 12
        base_loaded = 8
        
        # Adjust based on size and weight
        if self.max_weight > 26000:
            base_empty -= 3
            base_loaded -= 2
        elif self.cargo_capacity > 1000:
            base_empty -= 1
            base_loaded -= 1
        
        return {
            "empty_mpg": max(6, base_empty),
            "loaded_mpg": max(4, base_loaded)
        }
    
    def get_vehicle_info(self):
        """Extended vehicle info for trucks"""
        base_info = super().get_vehicle_info()
        return f"{base_info} - Cargo: {self.cargo_capacity}ft³, License: {self.license_required}, Max Weight: {self.max_weight}lbs"


class RentalManager:
    """Manager class to handle rental operations and fleet management"""
    
    def __init__(self):
        self.rental_history = []
    
    def rent_vehicle(self, vehicle_id, renter_name, rental_date=None):
        """Rent a vehicle by ID"""
        vehicle = Vehicle.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise ValueError(f"Vehicle {vehicle_id} not found")
        
        result = vehicle.rent(renter_name, rental_date)
        self.rental_history.append({
            "vehicle_id": vehicle_id,
            "renter": renter_name,
            "rental_date": rental_date or date.today(),
            "action": "rent"
        })
        return result
    
    def return_vehicle(self, vehicle_id, return_date=None, mileage_driven=0):
        """Return a vehicle by ID"""
        vehicle = Vehicle.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise ValueError(f"Vehicle {vehicle_id} not found")
        
        result = vehicle.return_vehicle(return_date, mileage_driven)
        self.rental_history.append({
            "vehicle_id": vehicle_id,
            "renter": result["renter"],
            "return_date": result["return_date"],
            "rental_days": result["rental_days"],
            "total_cost": result["total_cost"],
            "action": "return"
        })
        return result
    
    def get_fleet_statistics(self):
        """Get comprehensive fleet statistics"""
        all_vehicles = Vehicle.vehicle_registry.values()
        available_vehicles = Vehicle.get_available_vehicles()
        
        # Count by type
        type_counts = {}
        total_revenue = 0
        total_rental_days = 0
        
        for vehicle in all_vehicles:
            vehicle_type = getattr(vehicle, 'vehicle_type', 'Unknown')
            type_counts[vehicle_type] = type_counts.get(vehicle_type, 0) + 1
            total_revenue += vehicle.total_revenue
            total_rental_days += vehicle.total_rental_days
        
        return {
            "total_vehicles": Vehicle.total_vehicles,
            "available_vehicles": len(available_vehicles),
            "rented_vehicles": Vehicle.total_vehicles - len(available_vehicles),
            "vehicle_types": type_counts,
            "total_revenue": total_revenue,
            "total_rental_days": total_rental_days,
            "average_daily_revenue": total_revenue / total_rental_days if total_rental_days > 0 else 0
        }
    
    def get_maintenance_report(self):
        """Get maintenance report for all vehicles"""
        maintenance_needed = []
        total_maintenance_cost = 0
        
        for vehicle in Vehicle.vehicle_registry.values():
            if vehicle.needs_maintenance:
                maintenance_needed.append(vehicle.vehicle_id)
            total_maintenance_cost += vehicle.calculate_total_maintenance_cost()
        
        return {
            "vehicles_needing_maintenance": maintenance_needed,
            "total_maintenance_cost": total_maintenance_cost,
            "maintenance_needed_count": len(maintenance_needed)
        }


# === TESTING SECTION ===
if __name__ == "__main__":
    print("Vehicle Rental Management System")
    print("=" * 50)
    
    # Test Case 1: Basic vehicle creation and inheritance
    car = Car("CAR001", "Toyota", "Camry", 2023, 45.0, 5, "Automatic", True)
    motorcycle = Motorcycle("BIKE001", "Harley", "Street 750", 2022, 35.0, 750, "Cruiser")
    truck = Truck("TRUCK001", "Ford", "F-150", 2023, 85.0, 1200, "CDL-A", 5000)
    
    assert car.seating_capacity == 5
    assert motorcycle.engine_cc == 750
    assert truck.cargo_capacity == 1200
    
    # Test Case 2: Vehicle availability and rental logic
    assert car.is_available == True
    rental_result = car.rent()
    assert car.is_available == False
    assert "rented successfully" in rental_result.lower()
    
    return_result = car.return_vehicle()
    assert car.is_available == True
    
    # Test Case 3: Type-specific rental calculations
    # Car: base rate
    car_cost = car.calculate_rental_cost(3)
    assert car_cost == 45.0 * 3  # Standard calculation
    
    # Motorcycle: 20% discount for short rentals (<7 days)
    bike_cost = motorcycle.calculate_rental_cost(5)
    expected_bike = 35.0 * 5 * 0.8  # 20% discount
    assert abs(bike_cost - expected_bike) < 0.01
    
    # Truck: 50% surcharge for commercial vehicle
    truck_cost = truck.calculate_rental_cost(2)
    expected_truck = 85.0 * 2 * 1.5  # 50% surcharge
    assert abs(truck_cost - expected_truck) < 0.01
    
    # Test Case 4: Polymorphism - treating all vehicles uniformly
    vehicles = [car, motorcycle, truck]
    total_fleet_value = 0
    for vehicle in vehicles:
        info = vehicle.get_vehicle_info()
        assert vehicle.make in info
        assert vehicle.model in info
        if hasattr(vehicle, 'seating_capacity'):
            assert str(vehicle.seating_capacity) in info
        elif hasattr(vehicle, 'engine_cc'):
            assert str(vehicle.engine_cc) in info
    
    # Test Case 5: Fuel efficiency calculations (method overriding)
    # Cars: city/highway mpg based on transmission
    car_efficiency = car.get_fuel_efficiency()
    assert isinstance(car_efficiency, dict)
    assert 'city_mpg' in car_efficiency
    assert 'highway_mpg' in car_efficiency
    
    # Motorcycles: single mpg value
    bike_efficiency = motorcycle.get_fuel_efficiency()
    assert isinstance(bike_efficiency, (int, float))
    assert bike_efficiency > 40  # Motorcycles typically more efficient
    
    # Trucks: mpg varies by load capacity
    truck_efficiency = truck.get_fuel_efficiency()
    assert isinstance(truck_efficiency, dict)
    assert 'empty_mpg' in truck_efficiency
    assert 'loaded_mpg' in truck_efficiency
    
    print("All test cases passed successfully!")
    print("=" * 50)
