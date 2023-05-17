import pygame
from pygame import mixer
import columns_game as Game
import random


board_rows = 13
board_columns = 6
clock_time = 14

gem_list = ['S', 'T', 'V', 'W', 'X', 'Y', 'Z']


def _determine_gem_color(gem: str) -> (int, int, int):
    '''
    Determines the color of the specified jewel
    '''
    if gem == 'S':
        return (252, 209, 209)

    elif gem == 'T':
        return (211, 224, 220)

    elif gem == 'V':
        return (174, 225, 225)

    elif gem == 'W':
        return (255, 238, 187)

    elif gem == 'X':
        return (255, 220, 184)

    elif gem == 'Y':
        return (228, 186, 212)

    elif gem == 'Z':
        return (157, 173, 127)



class PyGame:
    def __init__(self):
        state = Game.GameState(board_rows, board_columns)

        self._state = state
        self._clock_time = clock_time
        self._running = True

        self._background_color = pygame.Color(205, 187, 167)
        self._board_color = pygame.Color(218, 208, 194)

        self._gem_buffer_y = 0.04
        self._gem_size = (1.0 - self._gem_buffer_y) / self._state.number_of_rows()
        self._gem_buffer_x = (1.0 - (self._gem_size * self._state.number_of_columns()))



    def start_game(self) -> None:
        '''
        Main function that starts the game
        '''
        pygame.init()

        try:
            clock = pygame.time.Clock()

            self._define_surface((600, 600))

            mixer.music.load('background_music.wav')
            mixer.music.set_volume(0.5)
            mixer.music.play(-1)

            self._match_sound = pygame.mixer.Sound('matching.wav')

            while self._running:
                clock.tick(clock_time)

                self._handle_events()

                self._clock_time -= 1

                if self._clock_time == 0:
                    self._game_time()
                    self._clock_time = clock_time

                self._draw_frame()


        finally:
            pygame.quit()



    def _game_time(self) -> None:
        '''
        Generates faller while game is running
        '''
        self._running = not self._state.clock()

        if not self._state.active_faller():
            contents = random.sample(gem_list, 3)
            column = random.randint(1, board_columns)

            self._state.generate_faller(column, contents)


    def _define_surface(self, size: (int, int)) -> None:
        '''
        Defines the surface window of the game
        '''
        self._surface = pygame.display.set_mode(size, pygame.RESIZABLE)



    def _handle_events(self) -> None:
        '''
        Handles the key events
        '''
        for event in pygame.event.get():
            self._handle_event(event)

        self._handle_keys()



    def _handle_event(self, event: pygame.event.EventType) -> None:
        '''
        Handles when to quit or resize video
        '''
        if event.type == pygame.QUIT:
            self._running = False

        elif event.type == pygame.VIDEORESIZE:
            self._define_surface(event.size)



    def _handle_keys(self) -> None:
        '''
        Handles what to do depending on what keys are pressed
        '''
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self._state.move_side(Game.left)

        if keys[pygame.K_RIGHT]:
            self._state.move_side(Game.right)

        if keys[pygame.K_SPACE]:
            self._state.rotate()



    def _draw_frame(self) -> None:
        '''
        Displays the current frame of the game
        '''
        self._surface.fill(self._background_color)
        self._draw_game_objects()

        pygame.display.flip()



    def _draw_game_objects(self) -> None:
        '''
        Displays the objects of the game
        '''
        top_left_x = self._frac_x_to_pixel_x((self._gem_buffer_x / 2))
        top_left_y = self._frac_y_to_pixel_y((self._gem_buffer_y / 2))

        width = self._frac_x_to_pixel_x((self._gem_size * self._state.number_of_columns()) - 0.001)
        height = self._frac_y_to_pixel_y((self._gem_size * self._state.number_of_rows()))

        outline_rect = pygame.Rect(top_left_x, top_left_y, width, height)
        pygame.draw.rect(self._surface, self._board_color, outline_rect, 0)

        for row in range(self._state.number_of_rows()):
            for column in range(self._state.number_of_columns()):
                self._draw_gem(row, column)



    def _draw_gem(self, row: int, column: int) -> None:
        '''
        Displays the specified gem
        '''
        gem = self._state.current_cell_contents(row, column)

        if gem is Game.empty:
            return

        raw_color = None
        state = self._state.current_cell_state(row, column)

        if state == Game.matching_cell:
            raw_color = (255, 255, 255)
            self._match_sound.play()

        else:
            raw_color = _determine_gem_color(gem)

        color = pygame.Color(raw_color[0], raw_color[1], raw_color[2])

        gem_x = (column * self._gem_size) + (self._gem_buffer_x / 2)
        gem_y = (row * self._gem_size) + (self._gem_buffer_y / 2)

        top_left_x = self._frac_x_to_pixel_x(gem_x)
        top_left_y = self._frac_y_to_pixel_y(gem_y)

        width = self._frac_x_to_pixel_x(self._gem_size)
        height = self._frac_y_to_pixel_y(self._gem_size)

        rect = pygame.Rect(top_left_x, top_left_y, width, height)

        pygame.draw.rect(self._surface, color, rect, 0)

        if state == Game.faller_stopped_cell:
            pygame.draw.rect(self._surface, pygame.Color(255, 255, 255), rect, 2)


    def _frac_x_to_pixel_x(self, frac_x: float) -> int:
        '''
        Converts fraction x value to pixel
        '''
        return self._frac_to_pixel(frac_x, self._surface.get_width())



    def _frac_y_to_pixel_y(self, frac_y: float) -> int:
        '''
        Converts fraction y value to pixel
        '''
        return self._frac_to_pixel(frac_y, self._surface.get_height())



    def _frac_to_pixel(self, frac: float, max_pixel: int) -> int:
        '''
        Converts fraction value to integer
        '''
        return int(frac * max_pixel)



if __name__ == '__main__':
    PyGame().start_game()
    
    
