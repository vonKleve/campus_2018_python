import random
from sys import exit
from enum import Enum

from player import Player

from game_map import Position
from game_map import Map

import savegame_utility

from logging_utility import logging_debug_decorator
from logging_utility import logging_info_decorator


class GameState(Enum):
    STARTING = 1,
    INGAME = 2,
    ENDING = 3


class GameWorld:
    """
    Game world.
    """

    def __init__(self):
        """
        Initializes player, game map.
        """
        mapSquareSize = random.randint(0, 20)
        mapSize = Position(mapSquareSize, mapSquareSize)
        startPos = \
            Position(random.randint(0, mapSquareSize),
                     random.randint(0, mapSquareSize))

        self.player = Player(position=startPos, hp=3, bag_counter=0)
        self.level = Map(size=mapSize, treasures=6, traps=6)

        self.actions = {
            "Up": "w",
            "Down": "s",
            "Left": "a",
            "Right": "d",

            "Save": "save",
            "Load": "load",

            "Help": "help",

            "Exit": "exit"
        }

        self.game_status = GameState.INGAME

    @logging_debug_decorator
    @logging_info_decorator
    def save(self):
        """
        Wrapper for savegame_utility save call.
        """
        savegame_utility.save(self.level.game_map, self.player.position)

    @logging_debug_decorator
    @logging_info_decorator
    def load(self):
        """
        Wrapper for savegame_utility load call.
        """
        self.level.game_map, self.player.position = savegame_utility.load()

    @logging_debug_decorator
    @logging_info_decorator
    def update_actions(self):
        """
        Returns:
            [str...] - actions performed.
        """
        input_str = input("Your turn\n")
        input_list = input_str.split(" ")

        actions = []
        for mstr in input_list:
            for name, key in self.actions.items():
                if key.casefold() == mstr.casefold():
                    actions.append(name)

        return actions

    @logging_debug_decorator
    @logging_info_decorator
    def print_hint(self):
        """
        If there is at least 1 treasure || trap in
        player's view - prints hint.
        """

        positions = [
            Position(self.player.position.x + self.level.view.x,
                     self.player.position.y),
            Position(self.player.position.x - self.level.view.x,
                     self.player.position.y),
            Position(self.player.position.x,
                     self.player.position.y + self.level.view.y),
            Position(self.player.position.x,
                     self.player.position.y - self.level.view.y)
        ]

        for position in positions:
            # check position
            position.clamp(min=Position(0, 0), max=self.level.size)
            # check cell
            if self.level.map_wrapper(position) == \
               self.level.reprs["treasure"]:
                print("There is a treasure near you.")

            if self.level.map_wrapper(position) == \
               self.level.reprs["trap"]:
                print("Careful! Trap is near you.")

    @logging_debug_decorator
    @logging_info_decorator
    def on_move_action(self, action):
        """
        Args:
            action (str): Up/Down/Left/Right move action.
        """
        if action != "Up" and \
                action != "Down" and \
                action != "Left" and \
                action != "Right":
                # raise excepption?
                pass

        self.player.move_with_restr(action, self.level.size)

        # on treasure || trap
        if self.level.map_wrapper(self.player.position) == \
                self.level.reprs["treasure"]:
            self.player.bag_counter += 1
        elif self.level.map_wrapper(self.player.position) == \
                self.level.reprs["trap"]:
            self.player.hp -= 1

        # perform win/loss check
        if self.player.hp <= 0:
            print("You lost, try again.")
            self.game_status = GameState.ENDING
        elif self.player.bag_counter >= 3:
            print("Congrats, winner!")
            self.game_status = GameState.ENDING

    @logging_debug_decorator
    @logging_info_decorator
    def on_action(self, action):
        """
        Changes game state on action.

        Args:
            action (str): name of the action from self.actions.
        """

        if action == "Up" or \
                action == "Down" or \
                action == "Left" or \
                action == "Right":
            self.on_move_action(action)
        elif action == "Save":
            self.save()
        elif action == "Load":
            self.load()
        elif action == "Help":
            print(self.actions)
        elif action == "Exit":
            self.game_status = GameState.ENDING

    @logging_debug_decorator
    @logging_info_decorator
    def on_ingame(self):
        print("updating on_ingame")

        print("updating wait for show")
        self.level.show(player_pos=self.player.position)

        print("updating wait for hint")
        self.print_hint()

        print("updating wait for update_actions")
        actions_performed = self.update_actions()

        print("updating wait for on_action")
        for action in actions_performed:
            self.on_action(action)

    @logging_debug_decorator
    @logging_info_decorator
    def on_ending(self):
        print("This world will miss you, goodbye!")

    @logging_debug_decorator
    @logging_info_decorator
    def update(self):
        """
        Game step.
        """
        # update actions
        print("updating update")
        if(self.game_status == GameState.INGAME):
            self.on_ingame()
        elif(self.game_status == GameState.ENDING):
            self.on_ending()
        else:
            # TO DO: raise exception
            exit(1)

    @logging_debug_decorator
    @logging_info_decorator
    def update_loop(self):
        """
        Wrapper around update.
        Exits when self.game_status == GameState.ENDING.
        """
        while self.game_status != GameState.ENDING:
            print("updating")
            self.update()