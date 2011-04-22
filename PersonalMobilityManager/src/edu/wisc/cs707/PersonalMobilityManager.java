package edu.wisc.cs707;

import android.app.TabActivity;
import android.content.Context;
import android.content.Intent;
import android.location.Criteria;
import android.location.LocationManager;
import android.os.Bundle;
import android.widget.TabHost;
import edu.wisc.cs707.io.StorageHandler;
import edu.wisc.cs707.net.XmlRpcClientHandler;
import edu.wisc.cs707.src.ModelInfo;
import edu.wisc.cs707.util.LocationController;

public class PersonalMobilityManager extends TabActivity {
	
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
    	
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        
        LocationController controller = LocationController.getInstance(getApplicationContext());
        LocationManager manager = (LocationManager)getSystemService(Context.LOCATION_SERVICE);
        
        XmlRpcClientHandler.getInstance(getApplicationContext());
        
        ModelInfo m = StorageHandler.getInstance(getApplicationContext()).loadModelInfo();
        
		Class<?> [] classes = new Class[] {
			PointsOfInterestActivity.class,
			ModelActivity.class,
			UserActivityLogActivity.class,
			DebugLogActivity.class,
		};
        String [][] labels = new String[][] {
        	new String[]{"poi", "PoI"},
        	new String[]{"stngs", "Settings"},
        	new String[]{"activity", "Activity"},
        	new String[]{"log", "Log"},
        };
        		
        TabHost tabHost = getTabHost();   
        
        for (int i = 0; i < classes.length; i++) {
        	 
            Intent intent = new Intent().setClass(this, classes[i]);
            TabHost.TabSpec tabSpec = tabHost.newTabSpec(labels[i][0]).setIndicator(labels[i][1]).setContent(intent);
            tabHost.addTab(tabSpec);
        }
    	
    	Criteria criteria = new Criteria();
    	criteria.setAccuracy(Criteria.ACCURACY_FINE);
    	criteria.setBearingRequired(false);
        criteria.setSpeedRequired(false);
        criteria.setSpeedRequired(false);
       
    	String provider = manager.getBestProvider(criteria, true);
    	manager.requestLocationUpdates(provider, (int)(60000 * m.getUpdateFrequency()), 0, controller);
    	
    	controller.set(manager, provider); // hack to work around threading issue.
    }
}