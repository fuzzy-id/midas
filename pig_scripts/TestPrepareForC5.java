import java.io.File;
import java.io.IOException;
import org.junit.Test;
import org.junit.Ignore;
import org.apache.pig.pigunit.PigTest;
import org.apache.pig.tools.parameters.ParseException;

public class TestPrepareForC5 {
    private PigTest test;
    private static final String SCRIPT = "prepare_for_c5.pig";

    @Test public void testSampleData() throws IOException, ParseException {
	String[] params = {
	    "samples=../test_data/samples",
	    "ids_to_sites=../test_data/ids_to_sites",
	    "tstamps_to_secs=../test_data/tstamps_to_secs",
	    "indicators=../test_data/indicators_pig",
	    "features=features",
	};

	PigTest test = new PigTest(SCRIPT, params);

	test.assertOutput("features", new File("../test_data/features.expected"));
    }
}