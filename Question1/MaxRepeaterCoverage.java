package Question1;
import java.util.HashMap;

public class MaxRepeaterCoverage {

    public static int maxPoints(int[][] points) {

        int n = points.length;
        if (n <= 2)
            return n;

        int result = 0;

        for (int i = 0; i < n; i++) {

            HashMap<String, Integer> map = new HashMap<>();
            int max = 0;

            for (int j = i + 1; j < n; j++) {

                int dx = points[j][0] - points[i][0];
                int dy = points[j][1] - points[i][1];

                // Handle vertical line
                if (dx == 0) {
                    dy = 1;
                }
                // Handle horizontal line
                else if (dy == 0) {
                    dx = 1;
                }
                // Reduce slope
                else {
                    int g = gcd(dx, dy);
                    dx = dx / g;
                    dy = dy / g;
                }

                String slope = dx + "," + dy;
                map.put(slope, map.getOrDefault(slope, 0) + 1);
                max = Math.max(max, map.get(slope));
            }

            result = Math.max(result, max + 1);
        }

        return result;
    }

    // GCD function
    public static int gcd(int a, int b) {
        if (b == 0)
            return a;
        return gcd(b, a % b);
    }

    public static void main(String[] args) {

        int[][] points1 = {{1,1}, {2,2}, {3,3}};
        int[][] points2 = {{1,4}, {2,3}, {3,2}, {4,1}, {5,3}, {1,1}};

        System.out.println(maxPoints(points1)); // 3
        System.out.println(maxPoints(points2)); // 4
    }
}
