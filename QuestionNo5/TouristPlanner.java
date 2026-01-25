package QuestionNo5;

import java.util.*;

class Spot {
    String name;
    int fee;
    Set<String> tags;

    Spot(String n, int f, String... t) {
        name = n;
        fee = f;
        tags = Set.of(t);
    }
}

public class TouristPlanner {
    public static void main(String[] args) {
        int budget = 500;
        Set<String> interest = Set.of("culture");

        List<Spot> spots = new ArrayList<>(List.of(
            new Spot("Pashupatinath", 100, "culture"),
            new Spot("Durbar Square", 100, "culture"),
            new Spot("Chandragiri", 700, "nature")
        ));

        spots.sort(Comparator.comparingInt(s -> s.fee));

        for (Spot s : spots) {
            if (Collections.disjoint(s.tags, interest)) continue;
            if (budget < s.fee) continue;

            budget -= s.fee;
            System.out.println("Visit: " + s.name);
        }
    }
}
