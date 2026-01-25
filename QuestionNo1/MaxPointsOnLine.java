import java.util.*;

public class MaxPointsOnLine {

    public static int maxPoints(int[][] points) {
        if (points.length <= 2) return points.length;

        int result = 0;

        for (int i = 0; i < points.length; i++) {
            Map<String, Integer> map = new HashMap<>();
            int same = 1;

            for (int j = i + 1; j < points.length; j++) {
                int dx = points[j][0] - points[i][0];
                int dy = points[j][1] - points[i][1];

                if (dx == 0 && dy == 0) {
                    same++;
                    continue;
                }

                int gcd = gcd(dx, dy);
                dx /= gcd;
                dy /= gcd;

                String slope = dx + "/" + dy;
                map.put(slope, map.getOrDefault(slope, 0) + 1);
            }

            int max = same;
            for (int val : map.values()) {
                max = Math.max(max, val + same);
            }

            result = Math.max(result, max);
        }
        return result;
    }

    private static int gcd(int a, int b) {
        return b == 0 ? a : gcd(b, a % b);
    }

    // MAIN METHOD
    public static void main(String[] args) {
        int[][] points = {
            {1, 1},
            {2, 2},
            {3, 3},
            {4, 4},
            {1, 2}
        };

        System.out.println("Max points on a line: " + maxPoints(points));
    }
}
