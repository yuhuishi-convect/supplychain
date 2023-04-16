"""
model.py defines the data strcuts to model supply chain network

"""
import dataclasses
from typing import List, Union, Dict, Tuple, Optional, Set
from abc import ABC
from dataclasses import dataclass, field


class Node(ABC):
    """
    Node class defines the basic node in the supply chain network
    """

    def get_maximum_throughput(self, product) -> float:
        """
        get_maximum_throughput returns the maximum throughput of the node
        """
        maximum_throughput = getattr(self, "maximum_throughput", None)
        if maximum_throughput is None:
            raise ValueError("maximum throughput is not defined")
        return maximum_throughput.get(product, float("inf"))

    def get_maximum_storage(self, product) -> float:
        """
        get_maximum_storage returns the maximum storage of the node
        """
        maximum_storage = getattr(self, "maximum_storage", None)
        if maximum_storage is None:
            raise ValueError("maximum storage is not defined")
        return maximum_storage.get(product, float("inf"))

    def get_additional_stock_cover(self, product) -> float:
        """
        get_additional_stock_cover returns the additional stock cover of the node
        """
        additional_stock_cover = getattr(self, "additional_stock_cover", None)
        if additional_stock_cover is None:
            raise ValueError("additional stock cover is not defined")
        return additional_stock_cover.get(product, 0)


@dataclass
class Location:
    """
    Location class defines the location of the node
    """

    latitude: float
    longitude: float
    name: Optional[str] = None


@dataclass
class Product:
    """
    A product
    """

    name: str
    unit_holding_cost: float

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Product):
            return self.name == __o.name
        return False


@dataclass
class Lane:
    """
    A lane is the connection between two nodes
    """

    origin: Node
    destination: Node
    fixed_cost: float = 0.0
    unit_cost: float = 0.0
    min_quantity: float = 0.0
    time: int = 0
    initial_arrivals: List[int] = field(default_factory=list)
    can_ship: List[bool] = field(default_factory=list)

    def can_ship_at(self, time: int) -> bool:
        """
        Check if units can be sent on the lane at the given time
        """
        if not self.can_ship:
            return True
        return self.can_ship[time]

    def get_arrivals(self, time: int) -> int:
        """
        Get the number of units arriving at the lane at the given time
        """
        if not self.initial_arrivals:
            return 0
        return self.initial_arrivals[time]


@dataclass
class Customer(Node):
    """
    A customer
    """

    name: str
    location: Location
    demands: Dict[Product, List[float]] = field(default_factory=dict)

    def add_product(self, product: Product, demand: List[float]):
        """
        Indicate that the customer wants to buy the product
        - product: the product
        - demand: the demand of the product
        """
        self.demands[product] = demand

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Customer):
            return self.name == __o.name
        return False

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Supplier(Node):
    """
    A supplier
    """

    name: str
    location: Location
    unit_cost: Dict[Product, float] = field(default_factory=dict)
    maximum_throughput: Dict[Product, float] = field(default_factory=dict)

    def add_product(
        self,
        product: Product,
        unit_cost: float,
        maximum_throughput: float = float("inf"),
    ):
        """
        Indicate that the supplier can provide the product
        - product: the product
        - unit_cost: the unit cost of the product
        - maximum_throughput: the maximum throughput of the product
        """
        self.unit_cost[product] = unit_cost
        self.maximum_throughput[product] = maximum_throughput

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Supplier):
            return self.name == __o.name
        return False

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Storage(Node):
    """
    A storage location
    """

    name: str
    location: Location
    fixed_cost: float = 0.0
    opening_cost: float = 0.0
    closing_cost: float = float("inf")
    initial_opened: bool = True
    initial_inventory: Dict[Product, float] = field(default_factory=dict)
    unit_handling_cost: Dict[Product, float] = field(default_factory=dict)
    maximum_throughput: Dict[Product, float] = field(default_factory=dict)
    maximum_units: Dict[Product, float] = field(default_factory=dict)
    additional_stock_cover: Dict[Product, float] = field(default_factory=dict)

    def add_product(
        self,
        product: Product,
        initial_inventory: float = 0.0,
        unit_handling_cost: float = 0.0,
        maximum_throughput: float = float("inf"),
        additional_stock_cover: float = 0.0,
    ):
        self.initial_inventory[product] = initial_inventory
        self.unit_handling_cost[product] = unit_handling_cost
        self.maximum_throughput[product] = maximum_throughput
        self.additional_stock_cover[product] = additional_stock_cover

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Storage):
            return self.name == __o.name
        return False

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Plant(Node):
    """
    A plant

    """

    name: str
    location: Location

    fixed_cost: float = 0.0
    opening_cost: float = 0.0
    closing_cost: float = float("inf")

    initial_opened: bool = True

    bill_of_materials: Dict[Product, Dict[Product, float]] = field(default_factory=dict)
    unit_cost: Dict[Product, float] = field(default_factory=dict)
    time: Dict[Product, int] = field(default_factory=dict)

    maximum_throughput: Dict[Product, float] = field(default_factory=dict)

    def add_product(
        self,
        product: Product,
        bill_of_materials: Dict[Product, float],
        unit_cost: float,
        maximum_throughput: float = float("inf"),
        time: int = 0,
    ):
        """
        Indicate that the plant can produce the product
        - product: the product
        - bill_of_materials: the amount of each product needed to produce the product
        - unit_cost: the unit cost of the product
        - maximum_throughput: the maximum number of units that can be produced in a time period
        - time: the production lead time
        """
        self.bill_of_materials[product] = bill_of_materials
        self.unit_cost[product] = unit_cost
        self.maximum_throughput[product] = maximum_throughput
        self.time[product] = time

    def has_bom(self, output: Product, input: Optional[Product] = None) -> bool:
        """
        Check if the plant has a bill of materials for the given product
        """
        if not input:
            return output in self.bill_of_materials

        return input in self.bill_of_materials[output]

    def get_bom(self, output: Product, input: Product) -> float:
        """
        Get the amount of the input product needed to produce the output product
        """
        return self.bill_of_materials[output][input]

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Plant):
            return self.name == __o.name
        return False

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Demand:
    """
    The demand a customer has for a product
    """

    customer: Customer
    product: Product
    service_level: float
    demand: List[float] = field(default_factory=list)
    probability: float = 1.0


@dataclass
class SupplyChainNetwork:
    products: Set[Product]
    storages: Set[Storage]
    suppliers: Set[Supplier]
    customers: Set[Customer]
    plants: Set[Plant]
    lanes: Set[Lane]
    demands: List[Demand]

    lanes_in: Dict[Node, List[Lane]] = field(default_factory=dict)
    lanes_out: Dict[Node, List[Lane]] = field(default_factory=dict)
    horizon: int = 1
    discount_factor: float = 1.0

    def add_demand(
        self,
        customer: Customer,
        product: Product,
        demand: List[float],
        service_level: float = 1.0,
    ) -> Demand:
        """
        Add customer demand for a product. The demand is specified for each time period.
        - demand: the amount of product demanded in each time period
        - service_level: indicates how many lost sales are allowed as a ratio of demand.
          No demand can be lost if the service level is 1.0
        """
        if service_level < 0.0 or service_level > 1.0:
            raise ValueError("Service level must be between 0 and 1")
        new_demand = Demand(customer, product, service_level, demand)
        self.demands.append(new_demand)
        return new_demand

    def add_product(self, product: Product) -> Product:
        """
        Add a product to the network
        """
        self.products.add(product)
        return product

    def add_customer(self, customer: Customer) -> Customer:
        """
        Add a customer to the network
        """
        self.customers.add(customer)
        return customer

    def add_supplier(self, supplier: Supplier) -> Supplier:
        """
        Add a supplier to the network
        """
        self.suppliers.add(supplier)
        return supplier

    def add_storage(self, storage: Storage) -> Storage:
        """
        Add a storage location to the network
        """
        self.storages.add(storage)
        return storage

    def add_lane(self, lane: Lane) -> Lane:
        """
        Add a lane to the network
        """
        self.lanes.add(lane)

        if lane not in self.lanes_in:
            self.lanes_in[lane.destination] = []
        self.lanes_in[lane.destination].append(lane)

        if lane not in self.lanes_out:
            self.lanes_out[lane.origin] = []
        self.lanes_out[lane.origin].append(lane)

        return lane

    def get_demand(self, customer: Customer, product: Product, time: int) -> float:
        """
        Get the demand for a product at a customer at a given time
        """
        for demand in self.demands:
            if demand.customer == customer and demand.product == product:
                return demand.demand[time]
        return 0.0

    def get_service_level(self, customer: Customer, product: Product) -> float:
        """
        Get the service level for a product at a customer
        """
        for demand in self.demands:
            if demand.customer == customer and demand.product == product:
                return demand.service_level
        return 1.0

    def get_lanes_in(self, node: Node) -> List[Lane]:
        """
        Get the lanes that lead to a node
        """
        return self.lanes_in.get(node, [])

    def get_lanes_out(self, node: Node) -> List[Lane]:
        """
        Get the lanes that leave a node
        """
        return self.lanes_out.get(node, [])
