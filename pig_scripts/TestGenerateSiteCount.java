import java.io.File;
import java.io.IOException;
import org.apache.pig.pigunit.PigTest;
import org.apache.pig.tools.parameters.ParseException;
import org.junit.Test;

public class TestGenerateSiteCount {
    private PigTest test;
    private static final String SCRIPT = "generate_site_count.pig";

    @Test public void testSomeProvidedData() throws IOException, ParseException {
	String[] args = {
	    "sites=provided_by_test",
	    "site_count=site_count",
	};
	PigTest test = new PigTest(SCRIPT, args);
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
	
    @Test public void testOnTestData() throws IOException, ParseException {
	String[] args = {
	    "sites=../test_data/sites/data",
	    "site_count=site_count",
	};
	PigTest test = new PigTest(SCRIPT, args);
	test.assertOutput(new File("../test_data/site_count.expected"));
    }
}