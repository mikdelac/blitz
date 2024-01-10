from game_message import *
from actions import *
import math

@dataclass
class AugmentedMeteor(Meteor):
    distance: float = None

    def __post_init__(self):
        self.distance = self.calculate_distance(self.position)

    @staticmethod
    def calculate_distance(position: Vector):
        ship_position = Vector(140, 400)   ## TO PATCH with cannon.position
        return math.sqrt( (position.x - ship_position.x)**2 + (position.y - ship_position.y)**2 )

@dataclass
class AugmentedCannon(Cannon):
    velocity: Vector = None

    def __post_init__(self):
        self.velocity = self.calculate_velocity(self.orientation)

    @staticmethod
    def calculate_velocity(orientation: float):
        return Vector(x=20 * math.cos(math.radians(orientation)), y=20 * math.sin(math.radians(orientation))) ## Magic numbers

class Bot:
    def __init__(self):
        self.direction = 1
        print("Initializing your super mega duper bot")


    # -------------------------
    """
    Getters for meteors by size
    """
    # -------------------------
    def get_small_meteors(self, game_message: GameMessage):
        """
        returns every small meteors
        """
        critere = lambda x: x.meteorType == MeteorType.Small
        return filter(critere, game_message.meteors)
    
    def get_medium_meteors(self, game_message: GameMessage):
        """
        returns every medium meteors
        """
        critere = lambda x: x.meteorType == MeteorType.Medium
        return filter(critere, game_message.meteors)

    def get_large_meteors(self, game_message: GameMessage):
        """
        returns every large meteors
        """
        critere = lambda x: x.meteorType == MeteorType.Large
        return list(filter(critere, game_message.meteors))


    # -------------------------
    """
    Getters for meteor by distance
    """
    # -------------------------
    def calculate_distance(self, meteor: Meteor) -> float:
        """
        Get closest meteor
        """


        pass


    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        if game_message.cannon.orientation >= 45:
            self.direction = -1
        elif game_message.cannon.orientation <= -45:
            self.direction = 1

        #augmented_meteors = [AugmentedMeteor(meteorType=meteor.meteorType, id=meteor.id, position=meteor.position, size=meteor.size, velocity=meteor.velocity) for meteor in self.get_large_meteors(game_message)]
        #closest_meteor = min(augmented_meteors, key=lambda x: x.distance)

        # -----------
        #   fonction qui découpe vitesse du missile en x et y
        # -----------
        augmented_cannon = AugmentedCannon(**vars(game_message.cannon))


        return [
            #LookAtAction(target=closest_meteor.position),
            RotateAction(angle=5 * self.direction),
            #ShootAction(),
        ]
