from game_message import *
from actions import *
import math

@dataclass
class AugmentedMeteor(Meteor):
    distance: float = None
    futur_positions: List[Vector] = None
    currentTick: int = None
    lockedIn: bool = False  # Cannon has that meteor in sight

    def __post_init__(self):
        self.distance = self.calculate_distance(self.position)
        self.futur_positions = self.get_futur_positions(self.position, self.velocity, self.currentTick)

    @staticmethod
    def calculate_distance(position: Vector):
        ship_position = Vector(140, 400)   ## TO PATCH with cannon.position
        if position.x < 140:
            return 99999
        else:
            return math.sqrt( (position.x - ship_position.x)**2 + (position.y - ship_position.y)**2 )

    @staticmethod
    def get_futur_positions(position: Vector, velocity: Vector, currentTick: int):
        return [Vector(x=position.x + velocity.x * i, y=position.y + velocity.y * i) for i in range(1, 1000 - (currentTick+1))]


@dataclass
class AugmentedCannon(Cannon):
    velocity: Vector = None
    futur_positions: List[Vector] = None  # futur positions for unlaunched missile at current tick
    currentTick: int = None

    def __post_init__(self):
        self.velocity = self.calculate_velocity(self.orientation)
        self.futur_positions = self. get_futur_positions(self.position, self.velocity, self.currentTick)

    @staticmethod
    def calculate_velocity(orientation: float):
        return Vector(x=20 * math.cos(math.radians(orientation)), y=20 * math.sin(math.radians(orientation))) ## Magic numbers

    @staticmethod
    def get_futur_positions(position: Vector, velocity: Vector, currentTick: int):
        return [Vector(x=position.x + velocity.x * i, y=position.y + velocity.y * i) for i in range(1, 1000 - (currentTick+1))]


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
    Cannon predictions (statistics and shit..)
        or law and physics.
    """
    # -------------------------
    def calculate_orientation(self, target: Vector, cannon: AugmentedCannon):
        """
        SOHCAHTOA MAGIC' BABY
        """
        side_opposed = abs(target.y - cannon.position.y)
        side_adjacent = abs(target.x - cannon.position.x)
        resulting_angle = math.atan(side_opposed / side_adjacent)

        if target.y > cannon.position.y:
            return resulting_angle
        elif target.y <= cannon.position.y:
            return resulting_angle * -1
        

    def get_killing_lookatVector(self, cannon: AugmentedCannon, target: AugmentedMeteor, game_message: GameMessage):
        """
        return true if a missile can kill its target, false otherwise
        1. For each futur_positions of given target
            Compare to get matching tick from cannon futur_positions and target futur_positions

            Problem with this approach: Missile velocity calculation happens at the beginning of a turn
            1.1 need to create a function that calculates missile velocity based on meteor futur_positions

        """
        can_kill = False
        tick = 0

        while can_kill == False:
            # Check how many ticks it takes for the missile to reach that meteor futur_position distance
            missile_numberOfTicks = -1
            if len(target.futur_positions) > tick:
                missile_numberOfTicks = round(target.calculate_distance(target.futur_positions[tick]) / game_message.constants.rockets.speed)

            if round(missile_numberOfTicks) != tick:
                tick += 1
            else:
                can_kill = True
        return target.futur_positions[tick]
        


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
        #   Création augmentedCannon
        # -----------
        augmented_cannon = AugmentedCannon(**vars(game_message.cannon), currentTick=game_message.tick)

        #closest_meteor = min(augmented_large_meteors, key=lambda x: x.distance)

        # Stratégie :
        # -----------
        #   1. Créer les positions futures des météorites
        # -----------
        if len(self.get_large_meteors(game_message)) != 0:
            augmented_large_meteors = [AugmentedMeteor(**vars(meteor), currentTick=game_message.tick) for meteor in self.get_large_meteors(game_message)]
            closest_meteor = min(augmented_large_meteors, key=lambda x: x.distance)

        # -----------
        #   2. Switch case :
        #   Pour le métérore le plus près:
        #       Si not lockedIn, lookat meteor position et lock-in
        #       Si lockedIn ET missile ne se rend pas à temps, rotate le cannon
        #       Si lockedIn ET not on cooldown ET missile se rend à temps, SHOOT
        # -----------
        #if closest_meteor.lockedIn == False:
        #    closest_meteor.lockedIn = True
        #    return [LookAtAction(target=closest_meteor.position)]
        #self.get_killing_lookatVector(augmented_cannon, closest_meteor, game_message)

        return [
            LookAtAction(target=self.get_killing_lookatVector(augmented_cannon, closest_meteor, game_message)),
            #RotateAction(angle=5 * self.direction),
            ShootAction(),
        ]
