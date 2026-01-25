package QuestionNo5;

class WeatherTask extends Thread {
    String city;

    WeatherTask(String city) {
        this.city = city;
    }

    public void run() {
        try {
            Thread.sleep(1000); // simulate API call
            System.out.println(city + ": Weather fetched");
        } catch (InterruptedException e) {}
    }
}

public class WeatherApp {
    public static void main(String[] args) {
        long start = System.currentTimeMillis();

        String[] cities = {"Kathmandu", "Pokhara", "Biratnagar", "Nepalgunj", "Dhangadhi"};
        for (String c : cities) new WeatherTask(c).start();

        long end = System.currentTimeMillis();
        System.out.println("Parallel fetch started in " + (end - start) + " ms");
    }
}
