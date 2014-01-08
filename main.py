from Tkinter import *
import random


class Application(Frame):

    #Constructor for Application class.
    def __init__(self, width, height, mine_count, master):
        Frame.__init__(self, master)
        self.master = master
        self.width = width
        self.height = height
        self.mine_count = mine_count 
        self.numbers = [one, two, three, four, five, six, seven, eight]
        self.tiles = []
        self.mines = []
        self.create_tiles()
        self.create_tile_mines()
        self.create_tile_nums()


    #Creates the grid of tiles, with dimensions self.height x self.width. 
    def create_tiles(self):
        for i in range(0, self.height):
            for j in range(0, self.width):
                button = Button(self, image=blank)
                button.bind("<Button-1>", self.handle_left_click)
                button.bind("<Button-3>", self.handle_right_click)
                button.grid(row=i, column=j)
                button.row = i
                button.column = j
                button.blank = True
                button.flag = False
                button.contents = 0
                self.tiles.append(button)


    #Assigns mines to certain tiles on a random basis. Number of mines
    #determined by self.mine_count.
    def create_tile_mines(self):
        num_mines = self.mine_count
        while num_mines > 0:
            mine_tile = random.choice(self.tiles)
            if mine_tile.contents != 10: 
                mine_tile.contents = 10
                self.mines.append(mine_tile)
                num_mines -= 1
             

    #Determines the number of mines neighboring each tile. This number
    #is what will appear when the blank tile is uncovered (clicked). If a 
    #tile has no neighboring mines, the uncovered tile will simply be blank.
    def create_tile_nums(self):
        for tile in self.tiles:
            if tile.contents != 10:
                count_mines = 0
                neighbors = self.find_neighbors(tile.row, tile.column)
                for n in neighbors:
                    if n.contents == 10:
                        count_mines += 1
                tile.contents = count_mines


    #Called when a tile is clicked with the left mouse button. The tile
    #in question is event.widget and is passed on to self.filter.
    def handle_left_click(self, event):
        self.filter(event.widget)
        if self.check_win():
            self.win_game()


    #Called when a tile is clicked with the right mouse button.
    #Determines which tile was selected from EVENT and marks that tile
    #with a flag if previously blank or blank if previously flagged.
    def handle_right_click(self, event):
        tile = event.widget
        if tile.flag == True:
            tile["image"] = blank
            tile.flag = False
        else:
            tile["image"] = flag 
            tile.flag = True


    #Determines how TILE should be dealt with based on its type (whether
    #it contains a mine, has no neighboring mines, or has at least one
    #mine).
    def filter(self, tile):
        r = tile.row
        c = tile.column

        #Tile contains a mine. (Here I'm designating mine tiles as having
        #tile.contents values of 10.)
        if tile.contents == 10:
            self.lose_game([tile])

        #Tile has no neighboring mines.
        elif tile.contents == 0:
            new = self.change_tile(tile, empty)
            self.tiles[self.convert(r, c)] = new
            tile["state"] = DISABLED
            neighbors = self.find_neighbors(r, c)
            for n in neighbors:
                if n.blank:
                    self.filter(n)

        #Tile has at least one neighboring mine.
        else:
            new = self.change_tile(tile, self.numbers[tile.contents - 1])
            self.tiles[self.convert(r, c)] = new
            tile["state"] = DISABLED


    #Changes the tile image when tile is clicked. E.g. transforms a blank
    #tile into a tile that display a number indicating the number of 
    #neighboring mines.
    def change_tile(self, tile, img):
        r = tile.row
        c = tile.column
        new = Label(self, image=img)
        new.row = r
        new.column = c
        new.blank = False
        new.grid(row=r, column=c)
        new["relief"] = SUNKEN
        if tile.contents != 10:
            new.bind("<Double-Button-1>", self.handle_double_click)
            new.contents = tile.contents
        return new


    #Called when player double-clicks a tile, which in this game serves
    #to uncover all neighboring non-mine squares at once if the player has 
    #in fact properly indentified and flagged all neighboring mines.
    def handle_double_click(self, event):
        tile = event.widget
        neighbors = self.find_neighbors(tile.row, tile.column)
        count_flags = 0
        for n in neighbors:
            if n.blank == True and n.flag == True:
                count_flags += 1

        #Double-click is a valid move
        if count_flags == tile.contents:
            lost = []
            for n in neighbors:
                position = self.convert(n.row, n.column)
                if n.contents == 10 and not n.flag:
                    lost.append(n)
                elif n.contents != 10 and n.blank and n.flag:
                    self.tiles[position] = self.change_tile(n, wrong)
    
            if len(lost) > 0:
                self.lose_game(lost)
                return

            for n in neighbors:
                if n.blank and n.contents != 10:
                    self.filter(n)

        if self.check_win():
            self.win_game()


    #Returns all neighboring tiles to the one at position (r, c).
    def find_neighbors(self, r, c):
        neighbors = []

        n_coord = [ [r-1, c-1], [r-1, c], [r-1, c+1], [r, c+1], \
                    [r+1, c+1], [r+1, c], [r+1, c-1], [r, c-1]  ]  

        for r,c in n_coord:
            if r >= 0 and r < self.height and c >= 0 and c < self.width: 
                neighbors.append(self.tiles[self.convert(r, c)])

        return neighbors
        

    #Given the position (ROW, COL) of a tile in the grid, finds tile's 
    #corresponding position in self.tiles.
    def convert(self, row, col):
        return self.width*row+col


    def check_win(self):
        count = 0
        for tile in self.tiles:
            if tile.blank:
                count += 1
        return count <= self.mine_count


    def win_game(self):
        for i in range(0, len(self.tiles)):
            tile = self.tiles[i]
            if tile.blank and tile.contents == 10:
                self.tiles[i] = self.change_tile(tile, flag)

    #Reveals the location of all mines when the game is lost.
    def lose_game(self, mine_tiles):
        for i in range(len(self.tiles)):
            tile = self.tiles[i]
            if tile.contents == 10:
                self.tiles[i] = self.change_tile(tile, mine)
            elif tile.blank:
                self.tiles[i] = self.change_tile(tile, blank)

        for i in range(len(mine_tiles)):
            self.tiles[i] = self.change_tile(mine_tiles[i], explode)

#        app = Application(30, 15, 40, self)
#        app.pack(side=BOTTOM)
#        app.mainloop()
#        root.destroy()


root = Tk()

#Load images.
empty = PhotoImage(file="images/empty.gif", width=20, height=20)
blank = PhotoImage(file="images/blank.gif", width=20, height=20)
mine = PhotoImage(file="images/mine.gif", width=20, height=20)
explode = PhotoImage(file="images/explode.gif", width=20, height=20)
wrong = PhotoImage(file="images/wrong.gif", width=20, height=20)
flag = PhotoImage(file="images/flag.gif", width=20, height=20)
one = PhotoImage(file="images/one.gif", width=20, height=20)
two = PhotoImage(file="images/two.gif", width=20, height=20)
three = PhotoImage(file="images/three.gif", width=20, height=20)
four = PhotoImage(file="images/four.gif", width=20, height=20)
five = PhotoImage(file="images/five.gif", width=20, height=20)
six = PhotoImage(file="images/six.gif", width=20, height=20)
seven = PhotoImage(file="images/seven.gif", width=20, height=20)
eight = PhotoImage(file="images/eight.gif", width=20, height=20)

root.title('Minesweeper')
app = Application(25, 10, 10, root)
app.pack(side=BOTTOM)
app.mainloop()
root.destroy()
