class StreakKeeper:

    def __init__(self):
        self.current_streak = 0
        self.streak_direction = 'NA'
        self.max_streaks = {}

    def get_current_streak(self):
        return Streak(self.current_streak, self.streak_direction)

    def get_max_streak(self, direction):
        if direction not in self.max_streaks:
            return Streak(0,direction)
        return Streak(self.max_streaks[direction], direction)

    def add_result(self,result):
        if result == self.streak_direction:
            self.current_streak += 1
        else:
            self.streak_direction = result
            self.current_streak = 1
        self.__update_max_streaks()

    def __update_max_streaks(self):
        if self.streak_direction not in self.max_streaks:
            self.max_streaks[self.streak_direction] = 0
        if self.current_streak > self.max_streaks[self.streak_direction]:
            self.max_streaks[self.streak_direction] = self.current_streak

class Streak:

    def __init__(self,len,name):
        self.length = len
        self.name = name

    def __str__(self) -> str:
        return str(self.name) + " " + str(self.length)
    
    def __repr__(self) -> str:
        return 'Member of Streak'
            
    def __lt__(self, other):
        if self.name == 'L' and other.name == 'W':
            return True
        if self.name == 'W' and other.name == 'L':
            return False
        if self.name == 'L':
            return self.length > other.length
        return other.length > self.length