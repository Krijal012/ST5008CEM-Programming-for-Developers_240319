import java.util.*;

public class WordBreak {

    public static List<String> wordBreak(String s, List<String> dict) {
        return dfs(s, new HashSet<>(dict), new HashMap<>());
    }

    private static List<String> dfs(String s, Set<String> dict, Map<String, List<String>> memo) {
        if (memo.containsKey(s)) return memo.get(s);

        List<String> result = new ArrayList<>();

        if (s.isEmpty()) {
            result.add("");
            return result;
        }

        for (String word : dict) {
            if (s.startsWith(word)) {
                List<String> sub = dfs(s.substring(word.length()), dict, memo);
                for (String str : sub) {
                    result.add(word + (str.isEmpty() ? "" : " " + str));
                }
            }
        }

        memo.put(s, result);
        return result;
    }

    // MAIN METHOD
    public static void main(String[] args) {
        String s = "catsanddog";
        List<String> dict = Arrays.asList("cat", "cats", "and", "sand", "dog");

        List<String> result = wordBreak(s, dict);
        System.out.println(result);
    }
}
