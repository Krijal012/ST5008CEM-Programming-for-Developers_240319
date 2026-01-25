package QuestionNo3;

public class StockProfit {

    public static int maxProfit(int k, int[] prices) {
        if (prices.length == 0 || k == 0) return 0;

        int[] dp = new int[prices.length];

        for (int t = 1; t <= k; t++) {
            int maxDiff = -prices[0];
            int[] newDp = new int[prices.length];

            for (int i = 1; i < prices.length; i++) {
                newDp[i] = Math.max(newDp[i - 1], prices[i] + maxDiff);
                maxDiff = Math.max(maxDiff, dp[i] - prices[i]);
            }
            dp = newDp;
        }
        return dp[prices.length - 1];
    }

    // MAIN METHOD
    public static void main(String[] args) {
        int[] prices = {3, 2, 6, 5, 0, 3};
        int k = 2;

        System.out.println("Max Profit: " + maxProfit(k, prices));
    }
}
