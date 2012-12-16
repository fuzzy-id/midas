import java.io.IOException;
import org.junit.Test;
import org.apache.pig.pigunit.PigTest;
import org.apache.pig.tools.parameters.ParseException;

public class TestAlexaTop1mGroupBySite {
    private PigTest test;
    private static final String SCRIPT = "alexa_top1m_group_by_site.pig";

    @Test public void testSampleData() throws IOException, ParseException {
	PigTest test = new PigTest(SCRIPT);
	
	String[] input = {
	    "foo.example.com\t1\t2012-12-16",
	    "foo.example.com\t1\t2012-12-15",
	    "foo.example.com\t1\t2012-12-14",
	    "bar.example.com\t2\t2012-12-16",
	    "bar.example.com\t2\t2012-12-15",
	    "bar.example.com\t2\t2012-12-14",
	};

	String[] output = {
	    "(foo.example.com,{(2012-12-16,1),(2012-12-15,1),(2012-12-14,1)})",
	    "(bar.example.com,{(2012-12-16,2),(2012-12-15,2),(2012-12-14,2)})",
	};

	test.assertOutput("top1m", input, "row", output);

    }
}