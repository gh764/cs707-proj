package edu.wisc.cs707;

import java.text.SimpleDateFormat;
import java.util.Date;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.TextView;
import edu.wisc.cs707.src.PointOfInterest;
import edu.wisc.cs707.util.IUserActivityListener;
import edu.wisc.cs707.util.LocationController;
import edu.wisc.cs707.util.LocationController.Snapshot;

public class UserActivityLogActivity extends Activity implements IUserActivityListener {

	private static final int MAX_ENTRIES = 255;
	private TextView log = null;
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
		
		LocationController controller = LocationController.getInstance(getApplicationContext());		
		LocationController.Snapshot snapshot = controller.getCurrentSnapshot();
		
		this.LogLocation(snapshot);
		
		controller.requestActivityUpdates(this);
	}
	
	SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss");
	private void LogLocation(Snapshot snapshot) {
		
		PointOfInterest poi = snapshot.getPoi();
		
		if (poi != null) {
			
			this.counter = ++this.counter % MAX_ENTRIES;
			if (this.counter == 0) {
				this.log.setText("");
			}
			
			this.log.append("Activity: " + snapshot.getActivity() + ";");
			this.log.append("Location: " + poi.getName() + "; Entered At: " +
					sdf.format(new Date(snapshot.getTimeEntered())));
			
			if (snapshot.getActivity() == edu.wisc.cs707.util.LocationController.Activity.Exited) {
				this.log.append("; Exited At: " + sdf.format(new Date(snapshot.getTimeExited())));
			}
			
			this.log.append("\n");
		} else {
			
		}
	}
	@Override
	public void onUserActivityUpdate(LocationController.Activity activity, Snapshot snapshot) {
		this.LogLocation(snapshot);
	}
}
