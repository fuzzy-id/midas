import java.io.IOException;
import java.io.File;
import org.junit.Test;
import org.apache.pig.pigunit.PigTest;
import org.apache.pig.tools.parameters.ParseException;

public class TestAlexaTop1mGroupBySite {
    private PigTest test;
    private static final String SCRIPT = "alexa_top1m_group_by_site.pig";

    @Test public void testSampleData() throws IOException, ParseException {
	String[] args = {
	    "input=provided_by_test",
	    "output=rows",
	};
	PigTest test = new PigTest(SCRIPT, args);
	String[] input = {
	    "foo.example.com\t2012-12-16\t1",
	    "foo.example.com\t2012-12-15\t1",
	    "foo.example.com\t2012-12-14\t1",
	    "bar.example.com\t2012-12-16\t2",
	    "bar.example.com\t2012-12-15\t2",
	    "bar.example.com\t2012-12-14\t2",
	};
	String[] output = {
	    "(bar.example.com,{(2012-12-16,2),(2012-12-15,2),(2012-12-14,2)})",
	    "(foo.example.com,{(2012-12-16,1),(2012-12-15,1),(2012-12-14,1)})",
	};
	test.assertOutput("top1m", input, "rows", output);
    }

    @Test public void testTestDataWithFixedOutput() throws IOException, ParseException {
	String[] args = {
	    "reducers=1",
	    "input=../test_data/alexa_files/",
	    "output=rows",
	};
	String[] expected = {
	    "(foo.example.com,{(2012-09-03,1)})",
	    "(baz.bar.example.com/path,{(2012-09-03,2),(2012-09-04,1)})",
	};
	PigTest test = new PigTest(SCRIPT, args);
	test.assertOutput("rows", expected);
    }

    @Test public void testTestData() throws IOException, ParseException {
	String[] args = {
	    "reducers=1",
	    "input=../test_data/alexa_files/",
	    "output=rows",
	};
	PigTest test = new PigTest(SCRIPT, args);
	test.assertOutput(new File("../test_data/alexa_grouped_by_site/expected_by_pig"));
    }
}