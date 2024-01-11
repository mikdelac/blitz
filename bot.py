from game_message import *
from actions import *
import math
import random

@dataclass
class AugmentedMeteor(Meteor):
    distance: float = None
    futur_positions: List[Vector] = None
    currentTick: int = None
    lockedIn: bool = False  # Cannon has that meteor in sight
    lastShot: bool = False # Cannon shot on meteor

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

meteor_list: List[AugmentedMeteor] = []

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
        return list(filter(critere, game_message.meteors))
    
    def get_medium_meteors(self, game_message: GameMessage):
        """
        returns every medium meteors
        """
        critere = lambda x: x.meteorType == MeteorType.Medium
        return list(filter(critere, game_message.meteors))

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

        while tick < len(target.futur_positions) and can_kill == False:
            # Check how many ticks it takes for the missile to reach that meteor futur_position distance
            missile_numberOfTicks = round(target.calculate_distance(target.futur_positions[tick]) / game_message.constants.rockets.speed)

            if round(missile_numberOfTicks) != tick:
                tick += 1
            else:
                can_kill = True
        if can_kill == True:
            return target.futur_positions[tick]
        pass
        


    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        # -----------
        #   Création augmentedCannon
        # -----------
        augmented_cannon = AugmentedCannon(**vars(game_message.cannon), currentTick=game_message.tick)

        # -----------
        #   Mise à jour liste globale pour field lastShot
        #   N'utilise le pas pour des opérations, juste réf sur lastShot
        # -----------
        for meteor in game_message.meteors:
            if not any(m.id == meteor.id for m in meteor_list):
                meteor_list.append(AugmentedMeteor(**vars(meteor), currentTick=game_message.tick))
        for meteor in meteor_list:
            if not any(m.id == meteor.id for m in game_message.meteors):
                meteor_list.remove(meteor)

        # -----------
        #   Création augmentedMeteor
        # -----------
        if len(game_message.meteors) != 0:
            augmented_meteors = [AugmentedMeteor(**vars(meteor), currentTick=game_message.tick) for meteor in game_message.meteors]

        # Stratégie :
        # -----------
        #   1. Switch case :
        # -----------
        if 'augmented_meteors' in locals():
            # Filter out meteors that are near the ship
            filtered_meteors = list(filter(lambda x: x.position.x > 1000, augmented_meteors))
            if len(filtered_meteors) != 0:
                # Choose the closest meteor, but if last tagged choose random
                closest_meteor = min(augmented_meteors, key=lambda x: x.distance)
                if list(filter(lambda x: x.id == closest_meteor.id, meteor_list))[0].lastShot == True:
                    if len(self.get_small_meteors(game_message) + self.get_medium_meteors(game_message)) != 0:
                        closest_meteor = random.choice([AugmentedMeteor(**vars(meteor), currentTick=game_message.tick) for meteor in self.get_small_meteors(game_message) + self.get_medium_meteors(game_message)])

                # Operations
                if augmented_cannon.cooldown > 0:
                    return [LookAtAction(target=self.get_killing_lookatVector(augmented_cannon, closest_meteor, game_message)), ShootAction()]
                elif augmented_cannon.cooldown == 0:
                    # Tag cleanup for every meteor
                    for meteor in meteor_list:
                        meteor.lastShot = False
                    # Tag the latest meteor
                    value = list(filter(lambda x: x.id == closest_meteor.id, meteor_list))[0]
                    value.lastShot = True
                    return [LookAtAction(target=self.get_killing_lookatVector(augmented_cannon, closest_meteor, game_message)), ShootAction()]



        return []

