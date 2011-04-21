package edu.wisc.cs707;

import java.text.DateFormat;
import java.text.DecimalFormat;
import java.util.Date;

import android.app.Activity;
import android.os.Bundle;
import android.widget.EditText;
import edu.wisc.cs707.io.StorageHandler;
import edu.wisc.cs707.src.ModelInfo;

public class ModelActivity extends Activity {

	private ModelInfo modelInfo = null;
	
	public void onCreate(Bundle savedInstanceState) {     
		super.onCreate(savedInstanceState);    
		setContentView(R.layout.model_info);
		
		this.modelInfo = StorageHandler.getInstance(getApplicationContext()).loadModelInfo();
		if (this.modelInfo != null) {
			this.bind2target();
		}
	}	

	private void setValue(int resource, Object value) {
        
    	String s = "";
    	
    	if (value instanceof Double) {
    		DecimalFormat fmt = new DecimalFormat("#.##");
    		s = fmt.format(value);
    	} else if (value instanceof Date) {
    		DateFormat df = DateFormat.getDateInstance(java.text.DateFormat.DEFAULT);
    		s = df.format((Date)value);
    	}
    	else {
    		s = value != null ? value.toString() : "";
    	}  	
    		
    	EditText t = (EditText)findViewById(resource);
    	t.setText(s);
    		
    }
	
	private void bind2target() {
		
		this.setValue(R.id.textEntryModelVersion, this.modelInfo.getVersion());
		this.setValue(R.id.textEntryModelCreationDate, this.modelInfo.getDateCreated());
		this.setValue(R.id.textEntryModelModificationDate, this.modelInfo.getDateUpdated());
		this.setValue(R.id.textEntryModelExpirationDate, this.modelInfo.getExpDate());
		this.setValue(R.id.textEntryModelWindowSize, this.modelInfo.getWindowSize());
		this.setValue(R.id.textEntryModelGranularity, this.modelInfo.getGranularity());
		
		//this.setValue(R.id.spinnerModelAggFx, this.modelInfo.getAggFx());
	}	
}