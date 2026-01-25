package QuestionNo6;

import java.util.*;

public class MaxFlow {
    static int bfs(int[][] r, int s, int t, int[] p) {
        boolean[] vis = new boolean[r.length];
        Queue<Integer> q = new LinkedList<>();
        q.add(s); vis[s] = true;

        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v = 0; v < r.length; v++) {
                if (!vis[v] && r[u][v] > 0) {
                    p[v] = u;
                    vis[v] = true;
                    q.add(v);
                }
            }
        }
        return vis[t] ? 1 : 0;
    }

    public static void main(String[] args) {
        int[][] cap = {
            {0,10,10,0},
            {0,0,2,8},
            {0,0,0,9},
            {0,0,0,0}
        };

        int s = 0, t = 3, flow = 0;
        int[] parent = new int[4];

        while (bfs(cap, s, t, parent) == 1) {
            int f = Integer.MAX_VALUE;
            for (int v = t; v != s; v = parent[v])
                f = Math.min(f, cap[parent[v]][v]);

            for (int v = t; v != s; v = parent[v]) {
                cap[parent[v]][v] -= f;
                cap[v][parent[v]] += f;
            }
            flow += f;
        }
        System.out.println("Max Flow = " + flow);
    }
}
