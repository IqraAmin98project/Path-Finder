import os
import random
import queue
import time
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox  # pip install CTkMessagebox
from PIL import ImageTk, Image  # pip install pillow

# Maze configuration
maze_rows = 15
maze_cols = 15
buttons = []
maze = []
user_path = []  # Global list to store the user's path
animation_speed = 50  # Default speed (ms)
solving_maze = False  # Flag to indicate if the maze is being solved
start_time = None  # Variable to store the start time
timer_running = False  # Flag to indicate if the timer is running
current_position = (0, 1)  # Starting position
extra_paths_probability = 0.0
root = None  # Initialize root variable

def initialize_maze():
    """Initialize the maze grid with walls ('#') everywhere."""
    global maze
    maze = [["#" for _ in range(maze_cols)] for _ in range(maze_rows)]

def create_buttons(maze_frame):
    """Create the grid of buttons representing the maze."""
    global buttons
    buttons.clear()  # Clear previous buttons
    for i in range(maze_rows):
        button_row = []
        for j in range(maze_cols):
            btn = ctk.CTkButton(master=maze_frame, text=" ", width=50, height=30, fg_color="white", corner_radius=0, command=lambda row=i, col=j: click_path(row, col))
            btn.grid(row=i, column=j)
            button_row.append(btn)
        buttons.append(button_row)

def click_path(i, j):
    global solving_maze, start_time, timer_running, user_path

    if not timer_running:
        if maze[i][j] == "O" or (i, j) == (1, 1):
            start_time = time.time()
            timer_running = True
            update_timer()

    if maze[i][j] == " " and not solving_maze:
        buttons[i][j].configure(fg_color="#b2f7ca")  # "#fae588" yellow color
        user_path.append((i, j))

    if maze[i][j] == "X" and timer_running:
        timer_running = False
        elapsed_time = time.time() - start_time
        timer_label.configure(text=f"Time: {elapsed_time:.2f} seconds")

        # Find the shortest path for comparison
        shortest_path = find_shortest_path(maze)
        
        # Add the official start and end points to user_path for accurate comparison
        adjusted_user_path = [(0, 1)] + user_path + [(14, 13)]

        # Check if the path is the shortest by comparing lengths and exact steps
        if adjusted_user_path == shortest_path or len(adjusted_user_path) == len(shortest_path):
            CTkMessagebox(title="Congratulations", message=f"You found the shortest path in {elapsed_time:.2f} seconds!", icon="check", option_1="Thanks!")
            reset_game()  # Reset game after finding the shortest path
        else:
            CTkMessagebox(title="Path Length", message="This is not the shortest path! Try again.", icon="cancel")
            reset_game()  # Reset game if not the shortest path

def move(event):
    global current_position
    i, j = current_position
    if event.keysym == "Up":
        new_position = (i - 1, j)
    elif event.keysym == "Down":
        new_position = (i + 1, j)
    elif event.keysym == "Left":
        new_position = (i, j - 1)
    elif event.keysym == "Right":
        new_position = (i, j + 1)
    else:
        return

    new_i, new_j = new_position
    if 0 <= new_i < len(maze) and 0 <= new_j < len(maze[0]):
        if maze[new_i][new_j] in [" ", "X"]:
            # Handle backtracking
            if (new_i, new_j) in user_path:
                # User is moving back to a previous cell
                buttons[current_position[0]][current_position[1]].configure(fg_color="white")
                user_path.remove(current_position)
            else:
                # Regular movement
                click_path(new_i, new_j)

            current_position = new_position
            if (new_i, new_j) not in user_path:
                user_path.append((new_i, new_j))

def reset_game():
    global current_position, user_path, solving_maze, timer_running, start_time, root  # Declare root as global

    # Reset the game state
    solving_maze = False
    timer_running = False
    start_time = None
    user_path.clear()  # Clear user path

    # Reset button colors
    for i in range(len(maze)):
        for j in range(len(maze[i])):
            if maze[i][j] == " ":
                buttons[i][j].configure(fg_color="white")  # Reset path cells to white

    # Reset current position to the starting position
    current_position = (0, 1)
    buttons[current_position[0]][current_position[1]].configure(bg_color="green")  # Highlight starting point

    # Rebind arrow keys for navigation
    root.bind("<Key>", move)

def update_timer():
    """Update the timer display if the timer is running."""
    if timer_running:
        elapsed_time = time.time() - start_time
        timer_label.configure(text=f"Time: {elapsed_time:.2f} seconds")
        timer_label.after(100, update_timer)  # Schedule update every 100 ms

def generate_maze():
    """Generate a random maze using the recursive backtracking algorithm, resetting the timer."""
    global start_time, timer_running, extra_paths_probability
    start_time = None  # Reset the timer on new maze generation
    timer_running = False
    timer_label.configure(text="Time: 0.00 seconds")  # Reset timer display

    initialize_maze()
    carve_passages(1, 1, extra_paths_probability)  # Start carving from (1, 1)
    
    # Set the start ('O') and end ('X') points
    maze[0][1] = "O"
    maze[maze_rows - 1][maze_cols - 2] = "X"
    
    update_maze_display()

def choose_difficulty(choice):
    global extra_paths_probability
    if choice == "Novice":
        extra_paths_probability = -0.9
    elif choice == "Amateur":
        extra_paths_probability = 0.4
    elif choice == "Master":
        extra_paths_probability = 1.0
    print(extra_paths_probability)
    return extra_paths_probability

def carve_passages(row, col, extra_paths_probability):
    """Carve passages in the maze using the recursive backtracking algorithm with extra paths."""
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, down, left, up
    random.shuffle(directions)

    for dr, dc in directions:
        new_row, new_col = row + 2 * dr, col + 2 * dc

        # Check if the new cell is within bounds and has not been carved
        if 0 <= new_row < maze_rows and 0 <= new_col < maze_cols and maze[new_row][new_col] == "#":
            # Carve the main path
            maze[row + dr][col + dc] = " "  # Carve passage between
            maze[new_row][new_col] = " "  # Carve new cell
            carve_passages(new_row, new_col, extra_paths_probability)  # Recursively carve next

            # Randomly add additional paths for extra connectivity
            if random.random() < extra_paths_probability:
                # Pick a random adjacent cell to open a passage if it is a wall
                adjacent_directions = [(dr, dc) for dr, dc in directions if maze[row + dr][col + dc] == "#"]
                if adjacent_directions:
                    extra_dr, extra_dc = random.choice(adjacent_directions)
                    maze[row + extra_dr][col + extra_dc] = " "

def update_maze_display():
    """Update the maze display after generating a new maze."""
    my_font = ctk.CTkFont(family="Candara", size=15)
    for i in range(maze_rows):
        for j in range(maze_cols):
            if maze[i][j] == "O":
                color = "#84e0a4"  # Start point
                buttons[i][j].configure(text="Begin!", font=my_font, text_color="black")
            elif maze[i][j] == "X":
                color = "#faa7c7"  # End point
                buttons[i][j].configure(text="End!", font=my_font, text_color="black")
            else:
                if maze[i][j] == " ":
                    color = "white"
                    buttons[i][j].configure(hover_color="#b2f7ca")
                else:
                    color = "#BCD4E6"
                    buttons[i][j].configure(state="disabled")
            buttons[i][ j].configure(fg_color=color)

def find_neighbors(maze, row, col):
    """Return valid neighboring positions (up, down, left, right)."""
    neighbors = []

    if row > 0:  # UP
        neighbors.append((row - 1, col))
    if row + 1 < len(maze):  # DOWN
        neighbors.append((row + 1, col))
    if col > 0:  # LEFT
        neighbors.append((row, col - 1))
    if col + 1 < len(maze[0]):  # RIGHT
        neighbors.append((row, col + 1))

    return neighbors

def find_start(maze):
    """Find the starting point in the maze (marked 'O')."""
    for i, row in enumerate(maze):
        for j, value in enumerate(row):
            if value == "O":
                return i, j
    return None

def find_path(maze):
    """Find the correct path from start ('O') to end ('X') in the maze."""
    start_pos = find_start(maze)
    if not start_pos:
        return []

    q = queue.Queue()
    q.put((start_pos, [start_pos]))  # Queue stores (current_position, path_so_far)

    visited = set()  # Using set to avoid revisiting positions
    visited.add(start_pos)

    while not q.empty():
        current_pos, path = q.get()
        row, col = current_pos

        if maze[row][col] == "X":
            return path  # Return the path when the end is reached

        # Explore neighbors (up, down, left, right)
        neighbors = find_neighbors(maze, row, col)
        for neighbor in neighbors:
            if neighbor not in visited:
                r, c = neighbor
                if maze[r][c] != "#":  # Not a wall
                    q.put((neighbor, path + [neighbor]))  # Add new path to the queue
                    visited.add(neighbor)

    return []  # No path found

def find_shortest_path(maze):
    """Find the shortest path from start ('O') to end ('X') in the maze using BFS."""
    start_pos = find_start(maze)
    if not start_pos:
        return []

    q = queue.Queue()
    q.put((start_pos, []))  # Queue stores (current_position, path_so_far)

    visited = set()  # To avoid revisiting positions
    visited.add(start_pos)

    while not q.empty():
        current_pos, path = q.get()
        row, col = current_pos

        if maze[row][col] == "X":
            return path + [current_pos]  # Return the path when the end is reached

        # Explore neighbors (up, down, left, right)
        neighbors = find_neighbors(maze, row, col)
        for neighbor in neighbors:
            if neighbor not in visited:
                r, c = neighbor
                if maze[r][c] != "#":  # Not a wall
                    q.put((neighbor, path + [current_pos]))  # Add new path to the queue
                    visited.add(neighbor)

    return []  # No path found

def solve_maze(root):
    """Solve the maze and animate the correct path step by step."""
    global solving_maze
    solving_maze = True  # Set flag to indicate solving in progress
    correct_path = find_path(maze)  # Find the correct path
    if correct_path:
        color_path_step_by_step(0, root, correct_path)  # Animate path coloring
    else:
        CTkMessagebox(title="No path Found", message="Uh-oh! It seems this maze has no solution. Try generating another maze.", icon="cancel")
    solving_maze = False  # Reset flag after solving

def color_path_step_by_step(index, root, path):
    """Color the correct path one step at a time."""
    if index < len(path):
        row, col = path[index]
        buttons[row][col].configure(fg_color="#c193db")  # Show progression
        root.after(animation_speed, color_path_step_by_step, index + 1, root, path)  # Schedule next step

def update_speed(value):
    """Update the animation speed based on user input."""
    global animation_speed
    animation_speed = int(value)

def main():
    """Initialize the tkinter GUI and set up the maze grid."""
    global maze_frame, timer_label, root
    root = ctk.CTk(fg_color="#99C1DE")  # Create the main window
    root.title("Path Finder: The Timed Challenge")
    root.resizable(False, False)  # Prevent window resizing ```python
    # Set root window icon
    root.iconpath = ImageTk.PhotoImage(file=os.path.join("maze.png"))
    root.wm_iconbitmap()
    root.iconphoto(False, root.iconpath)

    # Create custom font utility
    my_font = ctk.CTkFont(family="Candara", size=15)

    # Maze frame to hold the maze grid
    maze_frame = ctk.CTkFrame(root)
    maze_frame.pack(pady=10)

    # Timer display
    timer_img = Image.open("hourglass.png")
    timer_img_label = ctk.CTkLabel(root, text=" ", image=ctk.CTkImage(light_image=timer_img, dark_image=timer_img))
    timer_label = ctk.CTkLabel(root, text="Time: 0.00 seconds", font=my_font, text_color="black")
    timer_img_label.pack()
    timer_label.pack()

    # Instructions
    instructions = ctk.CTkLabel(root, text="Choose a difficulty level and click 'Generate Maze' for an appropriate random maze. Use Arrow keys to find the path.", font=my_font, text_color="black")
    instructions.pack()

    # Create maze grid
    create_buttons(maze_frame)
    generate_maze()  # Generate the initial random maze

    # Control frame to hold buttons and slider
    control_frame = ctk.CTkFrame(root, fg_color="#99C1DE")
    control_frame.pack(pady=10)

    # Generate button
    generate_button_img = Image.open("product.png")
    generate_button = ctk.CTkButton(control_frame, text="Generate Maze", 
                                    font=my_font, image=ctk.CTkImage(light_image=generate_button_img, dark_image=generate_button_img),
                                    corner_radius=32, command=lambda: [generate_maze(), reset_game()])
    generate_button.grid(row=0, column=0, padx=10)

    # Solve button
    solve_button_img = Image.open("path.png")
    solve_button = ctk.CTkButton(control_frame, text="Solve Maze", 
                                 font=my_font, image=ctk.CTkImage(light_image=solve_button_img, dark_image=solve_button_img),
                                 corner_radius=32, command=lambda: solve_maze(root))
    solve_button.grid(row=0, column=1, padx=10)

    # Difficulty Option Menu
    difficulty_combobox = ctk.CTkOptionMenu(
        control_frame,
        values=["Novice", "Amateur", "Master"],
        font=my_font,
        command=choose_difficulty
    )
    difficulty_combobox.grid(row=0, column=3, padx=5)

    # Single image for the Difficulty menu
    helmet_img = ctk.CTkImage(Image.open("helmet.png"))

    # Add image label next to the menu for icon effect
    icon_label = ctk.CTkLabel(control_frame, image=helmet_img, text="")
    icon_label.grid(row=0, column=2, padx=0)  # Positioned next to the menu

    # Speed slider label
    speed_label = ctk.CTkLabel(control_frame, text="Animation Speed:", font=my_font)
    speed_label.grid(row=1, column=0, padx=10)

    # Speed slider
    speed_slider = ctk.CTkSlider(master=control_frame, from_=10, to=200, orientation="horizontal", command=update_speed)
    speed_slider.set(animation_speed)  # Set initial value
    speed_slider.grid(row=1, column=1, padx=10)

    # Bind arrow keys to the move function
    root.bind("<Key>", move)

    # Run the Tkinter event loop to display the window
    root.mainloop()

main()
