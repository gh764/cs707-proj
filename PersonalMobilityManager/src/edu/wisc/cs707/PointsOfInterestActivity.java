/**
 * 
 */
package edu.wisc.cs707;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.text.DecimalFormat;

import android.app.AlertDialog;
import android.app.Dialog;
import android.app.ListActivity;
import android.location.Location;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.AdapterView.OnItemLongClickListener;
import android.widget.ArrayAdapter;
import android.widget.BaseAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ListView;
import edu.wisc.cs.cs707.io.StorageHandler;
import edu.wisc.cs707.src.PointOfInterest;
import edu.wisc.cs707.src.PointsOfInterest;
import edu.wisc.cs707.util.LocationController;

/**
 * @author Greig Hazell
 *
 */
public class PointsOfInterestActivity extends ListActivity implements OnItemClickListener, OnItemLongClickListener, OnClickListener {
	
	private static final int DIALOG_LOCTION_ID = 0;
	
	private BaseAdapter adapter = null;
	private PointsOfInterest pointsOfInterest = null;
	
	private PointOfInterest dlgPoi = new PointOfInterest();
    private PointOfInterest selected = null;
	
    private LocationController locationController = null;
	
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
				
		this.locationController = LocationController.getInstance(getApplicationContext());
		this.pointsOfInterest = this.locationController.getPointsOfInterest();
		this.adapter = new ArrayAdapter<PointOfInterest>(getApplicationContext(), R.layout.list_view,
				this.pointsOfInterest);
		
		setListAdapter(this.adapter);
		
		ListView lv = getListView();
		lv.setOnItemLongClickListener(this);
		lv.setOnItemClickListener(this);
	}
	
    private void setValue(Dialog parent, int resource, Object o, String propertyName) {
        
    	String s = "";
    	
    	if (o != null) {
    		try {
    			
    			Class<?> c = o.getClass();
    			Method m = c.getMethod("get" + propertyName, new Class[0]);
    			Object value = (Object)m.invoke(o, new Object[0]);
    			
    			if (value instanceof Double) {
    				DecimalFormat fmt = new DecimalFormat("#.##");
    				s = fmt.format(value);
    			} else {
    				s = value != null ? value.toString() : "";
    			}
    			
    		} catch (SecurityException e) {
    			e.printStackTrace();
    		} catch (NoSuchMethodException e) {
    			e.printStackTrace();
    		} catch (IllegalArgumentException e) {
    			e.printStackTrace();
    		} catch (IllegalAccessException e) {
    			e.printStackTrace();
    		} catch (InvocationTargetException e) {
    			e.printStackTrace();
    		}
    	}    	
    	
    	if (parent != null) { 
    		try {
    			EditText t = (EditText)parent.findViewById(resource);
    			if (t != null)
    				t.setText(s);
    		} catch (Exception e) {
    			e.printStackTrace();
    		}
    	}    	
    }
    
    private Object getValue(Dialog parent, int resource,String propertyName) {
    	
    	try {
    		Object o = parent.findViewById(resource);
			Method m = o.getClass().getMethod(propertyName, new Class[0]);
			return m.invoke(o, new Object[0]);
		} catch (SecurityException e) {
			e.printStackTrace();
		} catch (NoSuchMethodException e) {
			e.printStackTrace();
		} catch (IllegalArgumentException e) {
			e.printStackTrace();
		} catch (IllegalAccessException e) {
			e.printStackTrace();
		} catch (InvocationTargetException e) {
			e.printStackTrace();
		}
    	
    	return null;
    }
    
    private void bind2target(Dialog d, PointOfInterest poi) {
    	
    	dlgPoi.assign(poi != null ? poi : new PointOfInterest());
    	
    	setValue(d, R.id.LocationTextEntry, dlgPoi, "Name");
    	setValue(d, R.id.LatitudeTextEntry, dlgPoi, "Latitude");
    	setValue(d, R.id.LongitudeTextEntry, dlgPoi, "Longitude");
    	setValue(d, R.id.RadiusTextEntry, dlgPoi, "Radius");
    	setValue(d, R.id.AltitudeTextEntry, dlgPoi, "Altitude");
    	
    	((CheckBox)d.findViewById(R.id.MonitoredCheckBox)).setChecked(poi != null ?
    			poi.isMonitored() : false);
    }
    
    private void bind2source(Dialog d) {
    	
    	dlgPoi.setName(getValue(d, R.id.LocationTextEntry, "getText").toString());
    	dlgPoi.setMonitored((Boolean)getValue(d, R.id.MonitoredCheckBox, "isChecked"));
    	dlgPoi.setRadius(Integer.parseInt(getValue(d, R.id.RadiusTextEntry, "getText").toString()));
    }
    
    Dialog poiDialog = null;
    protected Dialog onCreateDialog(int id) {
    	
    	switch (id) {
    	case DIALOG_LOCTION_ID:
    		
    		LayoutInflater inflater = (LayoutInflater) getSystemService(LAYOUT_INFLATER_SERVICE);
    		View layout = inflater.inflate(R.layout.poi_screen, null, false);
    		AlertDialog.Builder builder = new AlertDialog.Builder(this);
    		builder.setView(layout);
    		poiDialog = builder.create();
    		
    		/* API level 8 required 
    		poiDialog.setOnShowListener(new OnShowListener() {
				
				@Override
				public void onShow(DialogInterface dialog) {
					bind_values((Dialog)dialog, selected);
				}
			});
    		*/
    		
    		int [] resources = new int[] {
    				R.id.ResetLocationBtn, R.id.LocateLocationBtn,
    				R.id.SaveLocationBtn, R.id.CloseLocationBtn };
    		
    		for (int r : resources) {
    			Button b = (Button)layout.findViewById(r);
    			b.setOnClickListener(this);
    		}
    		
    		break;
    	}
   
		return poiDialog;
    }
    
    private void onClickCurrentLocation(View v) {
    	Location l = this.locationController.getlastKnownLocation();
		if (l != null) {
			
			bind2source(poiDialog); // capture updates.
			dlgPoi.setLatitude(l.getLatitude());
			dlgPoi.setLongitude(l.getLongitude());
			dlgPoi.setAltitude((int)l.getAltitude());
			
			bind2target(poiDialog, dlgPoi);
			
		}
    }
    
    private void onClickCloseLocation(View v) {
		poiDialog.dismiss();
    }
    
    @SuppressWarnings("unchecked")
	public void onClickSaveLocation(View v) {
    	
    	PointOfInterest poi = this.selected;
    	
    	this.bind2source(this.poiDialog);
    	
    	if (this.selected != null) {
    		this.selected.assign(this.dlgPoi);
    		
    		int position = ((ArrayAdapter<PointOfInterest>)this.adapter).getPosition(selected);
    		((ArrayAdapter<PointOfInterest>)this.adapter).remove(selected);
    		((ArrayAdapter<PointOfInterest>)this.adapter).insert(selected, position); // TODO 
    		
    		this.selected = null;
    	} else {
    		poi = new PointOfInterest(this.dlgPoi);
    		((ArrayAdapter<PointOfInterest>)this.adapter).add(poi);
    		
    	}    	
    	StorageHandler.getInstance(getApplicationContext()).save(poi);
    	
    	bind2target(poiDialog, new PointOfInterest());
	}
    
    public void onClickClearLocation(View v) {
    	bind2target(poiDialog, new PointOfInterest());
    	selected = null;
    }
    
	@Override
	public void onClick(View v) {
		switch (v.getId()) {
		case R.id.ResetLocationBtn:
			this.onClickClearLocation(v);
			break;
		case R.id.LocateLocationBtn:
			this.onClickCurrentLocation(v);
			break;
		case R.id.SaveLocationBtn:
			this.onClickSaveLocation(v);
			break;
		case R.id.CloseLocationBtn:
			this.onClickCloseLocation(v);
			break;
		}
	}
		
	@Override
	public boolean onItemLongClick(AdapterView<?> parent, View view,
			int position, long id) {  

		if (position >= 0) {
			PointOfInterest p = (PointOfInterest)parent.getItemAtPosition(position);
			
			showDialog(DIALOG_LOCTION_ID);
			this.bind2target(poiDialog, p);
			this.selected = position > 0 ? p : null;
			return true;
		}
			
		return false;
	}

	@Override
	public void onItemClick(AdapterView<?> arg0, View arg1, int arg2, long arg3) {
		// TODO Auto-generated method stub
		
	} 
}