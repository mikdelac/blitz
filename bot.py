from game_message import *
from actions import *
import math

@dataclass
class AugmentedMeteor(Meteor):
    distance: float = None

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
    Getters for meteors by distance
    """
    # -------------------------
    def calculate_distance(self, meteor: Meteor) -> float:
        """
        Calculate distance between the ship and the meteor.
        """
        # Implement your distance calculation here
        ship_position = Vector(200, 400)

        return math.sqrt( (meteor.position.x - ship_position.x)**2 + (meteor.position.y - ship_position.y)**2 )

    def get_distances_meteors(self, meteors: List[Meteor]) -> List[AugmentedMeteor]:
        """
        For each meteor, calculate the distance from the ship and return a list of AugmentedMeteors.
        """
        augmented_meteors = [AugmentedMeteor(meteorType=meteor.meteorType, id=meteor.id, position=meteor.position, size=meteor.size, velocity=meteor.velocity, distance=self.calculate_distance(meteor)) for meteor in meteors]

        return augmented_meteors


    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        if game_message.cannon.orientation >= 45:
            self.direction = -1
        elif game_message.cannon.orientation <= -45:
            self.direction = 1

        test = self.get_distances_meteors(self.get_large_meteors(game_message))

        return [
            LookAtAction(target=game_message.meteors[0].position),
            #RotateAction(angle=15 * self.direction),
            ShootAction(),
        ]
