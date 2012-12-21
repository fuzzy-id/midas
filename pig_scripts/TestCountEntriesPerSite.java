import org.apache.pig.tools.parameters.ParseException;
import java.io.IOException;
import org.apache.pig.pigunit.PigTest;
import org.junit.Test;

public class TestAlexaCountRankPerSite {
    private PigTest test;
    private static final String SCRIPT = "alexa_count_rank_per_site.pig";

    @Test public void testSampleData() throws IOException, ParseException {
	PigTest test = new PigTest(SCRIPT);

	String[] input = {
	    "foo.example.com\t{(2012-12-16,1),(2012-12-15,1),(2012-12-14,1)}",
	    "bar.example.com\t{(2012-12-16,2),(2012-12-15,2),(2012-12-14,2)}",
	};

	String[] output = {
	    "(foo.example.com,3)",
	    "(bar.example.com,3)",
	};

	test.assertOutput("sites", input, "site_count", output);
    }
	
}