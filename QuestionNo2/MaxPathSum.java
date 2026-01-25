package QuestionNo2;

class TreeNode {
    int val;
    TreeNode left, right;

    TreeNode(int v) {
        val = v;
    }
}

public class MaxPathSum {
    static int max = Integer.MIN_VALUE;

    public static int maxPathSum(TreeNode root) {
        max = Integer.MIN_VALUE;
        dfs(root);
        return max;
    }

    private static int dfs(TreeNode node) {
        if (node == null) 
            return 0;

        int left = Math.max(0, dfs(node.left));
        int right = Math.max(0, dfs(node.right));

        max = Math.max(max, node.val + left + right);
        return node.val + Math.max(left, right);
    }

    // MAIN METHOD
    public static void main(String[] args) {
        TreeNode root = new TreeNode(1);
        root.left = new TreeNode(2);
        root.right = new TreeNode(3);

        System.out.println("Maximum Path Sum: " + maxPathSum(root));
    }
}
