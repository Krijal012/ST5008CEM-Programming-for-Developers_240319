package QuestionNo4;

import java.util.*;

class EnergySource {
    String name;
    int capacity;
    double cost;
    int start, end;

    EnergySource(String n, int c, double cost, int s, int e) {
        name = n;
        capacity = c;
        this.cost = cost;
        start = s;
        end = e;
    }

    boolean available(int hour) {
        return hour >= start && hour <= end;
    }
}

public class SmartGrid {
    public static void main(String[] args) {
        int hour = 6;
        int[] demand = {20, 15, 25}; // A, B, C
        int totalDemand = Arrays.stream(demand).sum();

        List<EnergySource> sources = new ArrayList<>(List.of(
            new EnergySource("Solar", 50, 1.0, 6, 18),
            new EnergySource("Hydro", 40, 1.5, 0, 24),
            new EnergySource("Diesel", 60, 3.0, 17, 23)
        ));

        sources.sort(Comparator.comparingDouble(s -> s.cost));

        for (EnergySource s : sources) {
            if (!s.available(hour) || totalDemand == 0) continue;

            int used = Math.min(s.capacity, totalDemand);
            totalDemand -= used;

            System.out.println(s.name + " used: " + used + " kWh");
        }
    }
}
