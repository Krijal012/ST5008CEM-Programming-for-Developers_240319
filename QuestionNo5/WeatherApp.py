import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import math
import itertools
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ============================================================================
# DATA MODELS
# ============================================================================

class TouristSpot:
    """Represents a tourist destination"""
    def __init__(self, name: str, latitude: float, longitude: float, 
                 entry_fee: int, open_time: str, close_time: str, tags: List[str]):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.entry_fee = entry_fee
        self.open_time = open_time
        self.close_time = close_time
        self.tags = set(tags)
    
    def distance_to(self, other: 'TouristSpot') -> float:
        """Calculate Euclidean distance to another spot"""
        dx = self.latitude - other.latitude
        dy = self.longitude - other.longitude
        return math.sqrt(dx * dx + dy * dy)
    
    def interest_score(self, user_interests: set) -> int:
        """Calculate interest match score"""
        return len(self.tags.intersection(user_interests)) * 10
    
    def __str__(self):
        return f"{self.name} (Rs.{self.entry_fee})"


class Itinerary:
    """Represents a complete travel itinerary"""
    def __init__(self, spots: List[TouristSpot], algorithm: str):
        self.spots = spots
        self.algorithm = algorithm
        self.total_cost = sum(spot.entry_fee for spot in spots)
        self.total_time = self._calculate_time()
    
    def _calculate_time(self) -> float:
        """Calculate total time including travel and visits"""
        if not self.spots:
            return 0.0
        
        # 2 hours per spot + travel time
        time = len(self.spots) * 2.0
        
        # Add travel time between spots
        for i in range(1, len(self.spots)):
            distance = self.spots[i-1].distance_to(self.spots[i])
            time += distance * 20  # Scale factor for travel time
        
        return time


# ============================================================================
# SAMPLE DATA
# ============================================================================

SAMPLE_SPOTS = [
    {
        "name": "Pashupatinath Temple",
        "latitude": 27.7104,
        "longitude": 85.3488,
        "entry_fee": 100,
        "open_time": "06:00",
        "close_time": "18:00",
        "tags": ["culture", "religious"]
    },
    {
        "name": "Swayambhunath Stupa",
        "latitude": 27.7149,
        "longitude": 85.2906,
        "entry_fee": 200,
        "open_time": "07:00",
        "close_time": "17:00",
        "tags": ["culture", "heritage"]
    },
    {
        "name": "Garden of Dreams",
        "latitude": 27.7125,
        "longitude": 85.3170,
        "entry_fee": 150,
        "open_time": "09:00",
        "close_time": "21:00",
        "tags": ["nature", "relaxation"]
    },
    {
        "name": "Chandragiri Hills",
        "latitude": 27.6616,
        "longitude": 85.2458,
        "entry_fee": 700,
        "open_time": "09:00",
        "close_time": "17:00",
        "tags": ["nature", "adventure"]
    },
    {
        "name": "Kathmandu Durbar Square",
        "latitude": 27.7048,
        "longitude": 85.3076,
        "entry_fee": 100,
        "open_time": "10:00",
        "close_time": "17:00",
        "tags": ["culture", "heritage"]
    },
    {
        "name": "Bhaktapur Durbar Square",
        "latitude": 27.6722,
        "longitude": 85.4298,
        "entry_fee": 150,
        "open_time": "10:00",
        "close_time": "17:00",
        "tags": ["culture", "heritage"]
    }
]


# ============================================================================
# OPTIMIZATION ALGORITHMS
# ============================================================================

class ItineraryOptimizer:
    """Handles different optimization algorithms"""
    
    @staticmethod
    def greedy_heuristic(spots: List[TouristSpot], budget: int, 
                        time_available: float, interests: set) -> Itinerary:
        """Greedy algorithm: Select best score/cost ratio spots"""
        
        # Score and sort spots
        scored_spots = []
        for spot in spots:
            interest_score = spot.interest_score(interests)
            cost_score = -spot.entry_fee / 100  # Penalize expensive spots
            total_score = interest_score + cost_score
            scored_spots.append((total_score, spot))
        
        scored_spots.sort(reverse=True, key=lambda x: x[0])
        
        # Greedy selection
        selected = []
        remaining_budget = budget
        remaining_time = time_available
        
        for score, spot in scored_spots:
            visit_time = 2.0  # Base visit time
            travel_time = 0.5  # Estimated travel
            
            if selected:
                last_spot = selected[-1]
                travel_time = last_spot.distance_to(spot) * 20
            
            total_time_needed = visit_time + travel_time
            
            if (spot.entry_fee <= remaining_budget and 
                total_time_needed <= remaining_time):
                selected.append(spot)
                remaining_budget -= spot.entry_fee
                remaining_time -= total_time_needed
        
        if not selected:
            return Itinerary([], "Greedy Heuristic")

        # The greedy selection is optimistic. Now, we find the best route for the
        # selected spots and ensure it fits the time constraint. If not, we
        # prune the selection.
        current_selection = list(selected)
        while len(current_selection) > 0:
            route = ItineraryOptimizer._nearest_neighbor(current_selection)
            itinerary = Itinerary(route, "Greedy Heuristic")
            
            # Check if this generated itinerary is valid
            if itinerary.total_time <= time_available:
                # This is a valid itinerary. Return it.
                return itinerary
            
            # If not valid, remove the last-added (and likely lowest value) spot and retry.
            # The 'selected' list is ordered by greedy choice, so pop() removes the worst one.
            current_selection.pop()
            
        # If no subset of the selected spots works, return an empty itinerary.
        return Itinerary([], "Greedy Heuristic")
    
    @staticmethod
    def _nearest_neighbor(spots: List[TouristSpot]) -> List[TouristSpot]:
        """Optimize route order using nearest neighbor TSP heuristic"""
        if len(spots) <= 1:
            return spots
        
        route = [spots[0]]
        remaining = set(spots[1:])
        
        while remaining:
            current = route[-1]
            nearest = min(remaining, key=lambda s: current.distance_to(s))
            route.append(nearest)
            remaining.remove(nearest)
        
        return route
    
    @staticmethod
    def brute_force(spots: List[TouristSpot], budget: int, 
                   time_available: float, interests: set) -> Itinerary:
        """Brute force: Try all possible subsets"""
        
        best_itinerary = Itinerary([], "Brute Force")
        best_score = -1
        
        # Try all subsets (limited to reasonable size)
        n = min(len(spots), 6)  # Limit for performance
        spots_subset = spots[:n]
        
        for r in range(1, n + 1):
            for subset in itertools.combinations(spots_subset, r):
                # First, check if the subset is within budget.
                subset_cost = sum(s.entry_fee for s in subset)
                if subset_cost > budget:
                    continue
                
                # Find the best permutation (shortest path) for this subset
                best_perm_for_subset = None
                min_time_for_subset = float('inf')

                for perm in itertools.permutations(subset):
                    # Manually calculate time to avoid creating Itinerary object repeatedly
                    perm_list = list(perm)
                    time = len(perm_list) * 2.0  # Visit time
                    for i in range(1, len(perm_list)):
                        distance = perm_list[i-1].distance_to(perm_list[i])
                        time += distance * 20 # Travel time
                    
                    if time < min_time_for_subset:
                        min_time_for_subset = time
                        best_perm_for_subset = perm_list
                
                # Now check the best path for this subset against time constraint
                if min_time_for_subset <= time_available:
                    # This subset and its best route are valid, calculate its score
                    score = sum(s.interest_score(interests) for s in best_perm_for_subset)
                    score -= subset_cost / 100  # Prefer cheaper
                    
                    if score > best_score:
                        best_score = score
                        best_itinerary = Itinerary(best_perm_for_subset, "Brute Force")
        
        return best_itinerary


# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

class TouristOptimizerGUI:
    """Main GUI Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 Tourist Spot Optimizer - Kathmandu Valley")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a2e')
        
        # Load data
        self.spots = [TouristSpot(**data) for data in SAMPLE_SPOTS]
        self.current_itinerary = None
        self.brute_force_itinerary = None
        
        # Color scheme
        self.colors = {
            'bg_dark': '#1a1a2e',
            'bg_medium': '#16213e',
            'bg_light': '#0f3460',
            'accent': '#e94560',
            'accent_light': '#ff6b81',
            'text_light': '#ffffff',
            'text_gray': '#aaaaaa',
            'success': '#00d2d3',
            'warning': '#ffd700',
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the complete user interface"""
        
        # ===== HEADER =====
        header_frame = tk.Frame(self.root, bg=self.colors['bg_medium'], height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        
        title_label = tk.Label(
            header_frame,
            text="🗺️ TOURIST SPOT OPTIMIZER",
            font=('Helvetica', 28, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent']
        )
        title_label.pack(pady=20)
        
        subtitle = tk.Label(
            header_frame,
            text="Plan Your Perfect Kathmandu Valley Tour",
            font=('Helvetica', 12),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_gray']
        )
        subtitle.pack()
        
        # ===== MAIN CONTAINER =====
        main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left Panel - Input
        self.create_input_panel(main_container)
        
        # Right Panel - Results
        self.create_results_panel(main_container)
    
    def create_input_panel(self, parent):
        """Create the left input panel"""
        
        input_frame = tk.Frame(parent, bg=self.colors['bg_medium'], width=450)
        input_frame.pack(side='left', fill='both', padx=(0, 10))
        
        # Title
        tk.Label(
            input_frame,
            text="📝 Your Preferences",
            font=('Helvetica', 18, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['success']
        ).pack(pady=15)
        
        # Time Available
        self._create_input_field(input_frame, "⏰ Time Available (hours):", 
                                 'time_var', '8')
        
        # Budget
        self._create_input_field(input_frame, "💰 Maximum Budget (Rs.):", 
                                 'budget_var', '1000')
        
        # Interests
        tk.Label(
            input_frame,
            text="🎯 Select Your Interests:",
            font=('Helvetica', 12, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_light']
        ).pack(pady=(20, 10))
        
        interest_frame = tk.Frame(input_frame, bg=self.colors['bg_medium'])
        interest_frame.pack(pady=5)
        
        self.interest_vars = {}
        interests = ['culture', 'nature', 'adventure', 'religious', 
                    'heritage', 'relaxation']
        
        for i, interest in enumerate(interests):
            var = tk.BooleanVar(value=(interest in ['culture', 'heritage']))
            self.interest_vars[interest] = var
            
            cb = tk.Checkbutton(
                interest_frame,
                text=interest.capitalize(),
                variable=var,
                font=('Helvetica', 11),
                bg=self.colors['bg_medium'],
                fg=self.colors['text_light'],
                selectcolor=self.colors['bg_light'],
                activebackground=self.colors['bg_medium'],
                activeforeground=self.colors['accent']
            )
            cb.grid(row=i//2, column=i%2, sticky='w', padx=10, pady=5)
        
        # Buttons
        button_frame = tk.Frame(input_frame, bg=self.colors['bg_medium'])
        button_frame.pack(pady=30)
        
        self._create_button(
            button_frame,
            "🚀 Generate Itinerary",
            self.generate_itinerary,
            self.colors['accent']
        ).pack(pady=10)
        
        self._create_button(
            button_frame,
            "⚡ Compare with Brute Force",
            self.compare_algorithms,
            self.colors['success']
        ).pack(pady=10)
        
        self._create_button(
            button_frame,
            "🔄 Reset",
            self.reset_form,
            self.colors['bg_light']
        ).pack(pady=10)
        
        # Available Spots
        tk.Label(
            input_frame,
            text="📍 Available Tourist Spots",
            font=('Helvetica', 14, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['warning']
        ).pack(pady=(20, 10))
        
        spots_text = scrolledtext.ScrolledText(
            input_frame,
            height=10,
            font=('Courier', 9),
            bg=self.colors['bg_light'],
            fg=self.colors['text_light'],
            wrap=tk.WORD
        )
        spots_text.pack(padx=20, pady=5, fill='both')
        
        for spot in self.spots:
            spots_text.insert(tk.END, 
                f"• {spot.name}\n"
                f"  Fee: Rs.{spot.entry_fee} | Tags: {', '.join(spot.tags)}\n\n"
            )
        spots_text.config(state='disabled')
    
    def create_results_panel(self, parent):
        """Create the right results panel"""
        
        results_frame = tk.Frame(parent, bg=self.colors['bg_medium'])
        results_frame.pack(side='right', fill='both', expand=True)
        
        # Title
        tk.Label(
            results_frame,
            text="📊 Your Optimized Itinerary",
            font=('Helvetica', 18, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['success']
        ).pack(pady=15)
        
        # Notebook for tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['bg_medium'])
        style.configure('TNotebook.Tab', 
                       background=self.colors['bg_light'],
                       foreground=self.colors['text_light'],
                       padding=[20, 10])
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', self.colors['text_light'])])
        
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Itinerary Details
        self.details_frame = tk.Frame(self.notebook, bg=self.colors['bg_dark'])
        self.notebook.add(self.details_frame, text='📋 Itinerary')
        
        self.details_text = scrolledtext.ScrolledText(
            self.details_frame,
            font=('Courier', 11),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_light'],
            wrap=tk.WORD
        )
        self.details_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 2: Map Visualization
        self.map_frame = tk.Frame(self.notebook, bg=self.colors['bg_dark'])
        self.notebook.add(self.map_frame, text='🗺️ Route Map')
        
        # Tab 3: Comparison
        self.comparison_frame = tk.Frame(self.notebook, bg=self.colors['bg_dark'])
        self.notebook.add(self.comparison_frame, text='⚖️ Comparison')
        
        self.comparison_text = scrolledtext.ScrolledText(
            self.comparison_frame,
            font=('Courier', 11),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_light'],
            wrap=tk.WORD
        )
        self.comparison_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def _create_input_field(self, parent, label_text, var_name, default_value):
        """Helper to create input field"""
        
        container = tk.Frame(parent, bg=self.colors['bg_medium'])
        container.pack(pady=10, padx=20, fill='x')
        
        tk.Label(
            container,
            text=label_text,
            font=('Helvetica', 12, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_light']
        ).pack(anchor='w')
        
        var = tk.StringVar(value=default_value)
        setattr(self, var_name, var)
        
        entry = tk.Entry(
            container,
            textvariable=var,
            font=('Helvetica', 14),
            bg=self.colors['bg_light'],
            fg=self.colors['text_light'],
            insertbackground=self.colors['text_light'],
            relief='flat',
            bd=0
        )
        entry.pack(fill='x', ipady=8, pady=5)
    
    def _create_button(self, parent, text, command, color):
        """Helper to create styled button"""
        
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=('Helvetica', 12, 'bold'),
            bg=color,
            fg=self.colors['text_light'],
            activebackground=self.colors['accent_light'],
            activeforeground=self.colors['text_light'],
            relief='flat',
            bd=0,
            padx=30,
            pady=12,
            cursor='hand2'
        )
        
        # Hover effects
        btn.bind('<Enter>', lambda e: btn.config(bg=self.colors['accent_light']))
        btn.bind('<Leave>', lambda e: btn.config(bg=color))
        
        return btn
    
    def get_selected_interests(self) -> set:
        """Get selected interest tags"""
        return {k for k, v in self.interest_vars.items() if v.get()}
    
    def generate_itinerary(self):
        """Generate itinerary using greedy heuristic"""
        
        try:
            # Get inputs
            time_available = float(self.time_var.get())
            budget = int(self.budget_var.get())
            interests = self.get_selected_interests()
            
            if not interests:
                messagebox.showwarning("Warning", 
                    "Please select at least one interest!")
                return
            
            # Run greedy algorithm
            self.current_itinerary = ItineraryOptimizer.greedy_heuristic(
                self.spots, budget, time_available, interests
            )
            
            # Display results
            self.display_itinerary()
            self.display_map()
            
            messagebox.showinfo("Success", 
                f"Found itinerary with {len(self.current_itinerary.spots)} spots!")
            
        except ValueError as e:
            messagebox.showerror("Error", 
                "Please enter valid numbers for time and budget!")
    
    def display_itinerary(self):
        """Display itinerary details"""
        
        self.details_text.config(state='normal')
        self.details_text.delete('1.0', tk.END)
        
        if not self.current_itinerary or not self.current_itinerary.spots:
            self.details_text.insert(tk.END, 
                "No itinerary generated yet.\n\n"
                "Please set your preferences and click 'Generate Itinerary'."
            )
            self.details_text.config(state='disabled')
            return
        
        itin = self.current_itinerary
        
        # Header
        self.details_text.insert(tk.END, 
            "═" * 60 + "\n"
            f"  {itin.algorithm.upper()}\n"
            "═" * 60 + "\n\n"
        )
        
        # Spots
        for i, spot in enumerate(itin.spots, 1):
            self.details_text.insert(tk.END, 
                f"{i}. {spot.name}\n"
                f"   💰 Entry Fee: Rs.{spot.entry_fee}\n"
                f"   ⏰ Hours: {spot.open_time} - {spot.close_time}\n"
                f"   🏷️  Tags: {', '.join(spot.tags)}\n"
                f"   📍 Location: ({spot.latitude:.4f}, {spot.longitude:.4f})\n"
            )
            
            if i > 1:
                prev_spot = itin.spots[i-2]
                distance = prev_spot.distance_to(spot)
                travel_time = distance * 20
                self.details_text.insert(tk.END, 
                    f"   🚗 Travel from previous: {distance:.3f} km "
                    f"(~{travel_time:.1f} min)\n"
                )
            
            self.details_text.insert(tk.END, "\n")
        
        # Summary
        self.details_text.insert(tk.END, 
            "─" * 60 + "\n"
            f"📊 SUMMARY\n"
            "─" * 60 + "\n"
            f"Total Spots: {len(itin.spots)}\n"
            f"Total Cost: Rs.{itin.total_cost}\n"
            f"Total Time: {itin.total_time:.1f} hours\n"
            f"Algorithm: {itin.algorithm}\n"
            "─" * 60 + "\n\n"
            "💡 OPTIMIZATION EXPLANATION:\n"
            "The greedy heuristic selected spots based on:\n"
            "1. Interest match score (your preferences)\n"
            "2. Cost-efficiency (lower fees preferred)\n"
            "3. Route optimization (nearest neighbor for travel)\n"
            "4. Budget and time constraints\n"
        )
        
        self.details_text.config(state='disabled')
    
    def display_map(self):
        """Display route map visualization"""
        
        # Clear previous map
        for widget in self.map_frame.winfo_children():
            widget.destroy()
        
        if not self.current_itinerary or not self.current_itinerary.spots:
            tk.Label(
                self.map_frame,
                text="No route to display",
                font=('Helvetica', 14),
                bg=self.colors['bg_dark'],
                fg=self.colors['text_gray']
            ).pack(expand=True)
            return
        
        # Create figure
        fig = Figure(figsize=(10, 8), facecolor='#1a1a2e')
        ax = fig.add_subplot(111, facecolor='#16213e')
        
        spots = self.current_itinerary.spots
        
        # Plot route
        lats = [s.latitude for s in spots]
        lons = [s.longitude for s in spots]
        
        # Draw lines
        ax.plot(lons, lats, 'o-', color='#e94560', linewidth=2, 
               markersize=12, markeredgecolor='white', markeredgewidth=2)
        
        # Add labels
        for i, spot in enumerate(spots, 1):
            ax.annotate(
                f"{i}. {spot.name}",
                xy=(spot.longitude, spot.latitude),
                xytext=(10, 10),
                textcoords='offset points',
                fontsize=9,
                color='white',
                bbox=dict(boxstyle='round,pad=0.5', 
                         facecolor='#0f3460', alpha=0.8)
            )
        
        ax.set_xlabel('Longitude', color='white', fontsize=12)
        ax.set_ylabel('Latitude', color='white', fontsize=12)
        ax.set_title('Your Optimized Route', color='#00d2d3', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, color='gray')
        ax.tick_params(colors='white')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.map_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def compare_algorithms(self):
        """Compare greedy with brute force"""
        
        try:
            # Get inputs
            time_available = float(self.time_var.get())
            budget = int(self.budget_var.get())
            interests = self.get_selected_interests()
            
            if not interests:
                messagebox.showwarning("Warning", 
                    "Please select at least one interest!")
                return
            
            # Run both algorithms
            self.current_itinerary = ItineraryOptimizer.greedy_heuristic(
                self.spots, budget, time_available, interests
            )
            
            self.brute_force_itinerary = ItineraryOptimizer.brute_force(
                self.spots, budget, time_available, interests
            )
            
            # Display comparison
            self.display_comparison()
            
            # Switch to comparison tab
            self.notebook.select(self.comparison_frame)
            
            messagebox.showinfo("Comparison Complete", 
                "Algorithm comparison completed!")
            
        except ValueError:
            messagebox.showerror("Error", 
                "Please enter valid numbers for time and budget!")
    
    def display_comparison(self):
        """Display algorithm comparison"""
        
        self.comparison_text.config(state='normal')
        self.comparison_text.delete('1.0', tk.END)
        
        greedy = self.current_itinerary
        brute = self.brute_force_itinerary
        
        self.comparison_text.insert(tk.END, 
            "═" * 70 + "\n"
            "  ALGORITHM COMPARISON REPORT\n"
            "═" * 70 + "\n\n"
            "📊 GREEDY HEURISTIC:\n"
            f"  Spots Visited: {len(greedy.spots)}\n"
            f"  Total Cost: Rs.{greedy.total_cost}\n"
            f"  Total Time: {greedy.total_time:.1f} hours\n"
            f"  Spots: {', '.join(s.name for s in greedy.spots)}\n\n"
            "⚡ BRUTE FORCE (Optimal on subset):\n"
            f"  Spots Visited: {len(brute.spots)}\n"
            f"  Total Cost: Rs.{brute.total_cost}\n"
            f"  Total Time: {brute.total_time:.1f} hours\n"
            f"  Spots: {', '.join(s.name for s in brute.spots)}\n\n"
            "─" * 70 + "\n"
            "📈 METRICS COMPARISON:\n"
            "─" * 70 + "\n"
            f"Spot Count Difference: {abs(len(greedy.spots) - len(brute.spots))}\n"
            f"Cost Difference: Rs.{abs(greedy.total_cost - brute.total_cost)}\n"
            f"Time Difference: {abs(greedy.total_time - brute.total_time):.1f} hours\n\n"
            "─" * 70 + "\n"
            "🔍 ANALYSIS:\n"
            "─" * 70 + "\n"
        )
        
        # Performance analysis
        if len(greedy.spots) >= len(brute.spots):
            self.comparison_text.insert(tk.END, 
                "✅ Greedy found equal or more spots than brute force!\n"
            )
        else:
            self.comparison_text.insert(tk.END, 
                "⚠️  Brute force found more spots (guaranteed optimal on subset)\n"
            )
        
        self.comparison_text.insert(tk.END, 
            "\n💡 TRADE-OFF DISCUSSION:\n"
            "• Greedy Heuristic:\n"
            "  - Fast: O(n log n) time complexity\n"
            "  - Scalable: Works well with many spots\n"
            "  - Near-optimal: Usually finds good solutions\n"
            "  - Real-time: Instant results\n\n"
            "• Brute Force:\n"
            "  - Optimal: Guaranteed best solution\n"
            "  - Slow: O(2^n × n!) exponential time\n"
            "  - Limited: Only practical for <7 spots\n"
            "  - Comprehensive: Tries all possibilities\n\n"
            "🎯 RECOMMENDATION:\n"
            "For real-world use with many tourist spots, greedy heuristic\n"
            "provides excellent results with instant performance!\n"
        )
        
        self.comparison_text.config(state='disabled')
    
    def reset_form(self):
        """Reset all inputs"""
        self.time_var.set('8')
        self.budget_var.set('1000')
        for var in self.interest_vars.values():
            var.set(False)
        self.interest_vars['culture'].set(True)
        self.interest_vars['heritage'].set(True)
        
        self.details_text.config(state='normal')
        self.details_text.delete('1.0', tk.END)
        self.details_text.insert(tk.END, "Form reset. Ready for new input!")
        self.details_text.config(state='disabled')


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Launch the application"""
    root = tk.Tk()
    app = TouristOptimizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()