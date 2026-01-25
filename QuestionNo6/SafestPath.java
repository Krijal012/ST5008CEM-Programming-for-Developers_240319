package QuestionNo6;

import java.util.*;

class Edge {
    int v;
    double w;
    Edge(int v, double w) { this.v = v; this.w = w; }
}

public class SafestPath {
    public static void main(String[] args) {
        List<List<Edge>> g = new ArrayList<>();
        for (int i = 0; i < 3; i++) g.add(new ArrayList<>());

        g.get(0).add(new Edge(1, -Math.log(0.9)));
        g.get(1).add(new Edge(2, -Math.log(0.95)));

        double[] dist = new double[3];
        Arrays.fill(dist, Double.MAX_VALUE);
        dist[0] = 0;

        PriorityQueue<Integer> pq = new PriorityQueue<>(Comparator.comparingDouble(i -> dist[i]));
        pq.add(0);

        while (!pq.isEmpty()) {
            int u = pq.poll();
            for (Edge e : g.get(u)) {
                if (dist[u] + e.w < dist[e.v]) {
                    dist[e.v] = dist[u] + e.w;
                    pq.add(e.v);
                }
            }
        }

        System.out.println("Safest probability = " + Math.exp(-dist[2]));
    }
}
