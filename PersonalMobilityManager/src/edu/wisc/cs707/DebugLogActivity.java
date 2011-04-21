package edu.wisc.cs707;

import android.app.Activity;
import android.location.Location;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.TextView;
import edu.wisc.cs707.util.ILogger;
import edu.wisc.cs707.util.LocationController;
import edu.wisc.cs707.util.LocationController.Snapshot;

public class DebugLogActivity extends Activity implements ILogger {
	
	private static final int MAX_ENTRIES = 255;
	
	private TextView log;
	private int counter = 0;
	
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_log);
		
		this.log = (TextView)findViewById(R.id.textViewActivityLog);
		((Button)findViewById(R.id.clr_activity_log_btn)).setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) { 
				log.setText("");
			}
		});
		
		LocationController c = LocationController.getInstance(getApplicationContext());
		c.log(this);
		
		this.log(c.getlastKnownLocation());
	}
	@Override
	public void log(Snapshot snapshot) {
		// TODO Auto-generated method stub
		
	}
	@Override
	public void log(Location location) {
		if (location != null) {
			this.log("LocationUpdate[time:" + location.getTime() +
				"; lat:" + location.getLatitude() + "; long:" + location.getLongitude() + 
				"; accuracy:" + location.getAccuracy() +
				"; provider:" + location.getProvider() + "]\n");
		}
	}
	@Override
	public void log(String caption, String text) {
		this.log.append(caption +"[" + text + "]\n");
	}
	@Override
	public void log(Object o) {
		// TODO Auto-generated method stub
		
	}
	
	private void log(String text) {
		this.counter = (this.counter + 1) % MAX_ENTRIES;
		if (this.counter == 0) {
			this.log.setText("");
		}
		
		this.log.append(text);
	}
}