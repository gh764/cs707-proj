package edu.wisc.cs707.io;

import java.io.EOFException;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;

import android.content.Context;
import edu.wisc.cs707.src.ModelInfo;


public class DataFileStorageHandler {

	private static final String MODEL_FILENAME = "model.dat";
	
	private Context mContext;
	public DataFileStorageHandler(Context context) {
		this.mContext = context;
	}
	
	boolean save(ModelInfo model) {
		
		try {
			
			FileOutputStream fileStream = this.mContext.openFileOutput(MODEL_FILENAME, 
					Context.MODE_PRIVATE);
			ObjectOutputStream outputStream = new ObjectOutputStream(fileStream);
			
			outputStream.writeObject(model);
			outputStream.close();
			
			return true;
		} catch (IOException e) {
		}
		
		return false;
	}
	
	ModelInfo loadModelInfo() throws FileNotFoundException, 
		EOFException {
		
		ModelInfo m = null;
		
		ObjectInputStream inputStream = null;
		
		try {
			
			FileInputStream fileStream = this.mContext.openFileInput(MODEL_FILENAME);			
			inputStream = new ObjectInputStream(fileStream);
			
			m = (ModelInfo)inputStream.readObject();
		} catch (EOFException e) {
			throw e;
		} catch (FileNotFoundException e) {
			throw e;
		} catch (IOException e) {
			
		} catch (ClassNotFoundException e) {
			
		} finally {
			try {
				if (inputStream != null) 
					inputStream.close();
			} catch (IOException e) {
				
			}
		}
		
		return m;
	}
	
	/*
	PointsOfInterest loadPointsOfInterest(Context context, String filename) {
		PointsOfInterest p = new PointsOfInterest();
		
		ObjectInputStream ois = null;
		
		try {
			PointOfInterest poi = null;
			FileInputStream fis = context.openFileInput(filename);			
			ois = new ObjectInputStream(fis);
			while ((poi = (PointOfInterest)ois.readObject()) != null) {
				p.add(poi);
			}
		} catch (EOFException e) {
			
		} catch (FileNotFoundException e) {
			
		} catch (IOException e) {
			
		} catch (ClassNotFoundException e) {
			
		} finally {
			try {
				if (ois != null) 
					ois.close();
			} catch (IOException e) {
				
			}
		}
		
		return p;
	}
	
	void savePointsOfInterest(Context c, String filename, PointsOfInterest p) {
		try {
			FileOutputStream fileStream = c.openFileOutput(filename, Context.MODE_PRIVATE);
			ObjectOutputStream outputStream = new ObjectOutputStream(fileStream);
			
			for(int i = 1; i < p.size(); i++) {
				outputStream.writeObject(p.get(i));
			}
			
			outputStream.close();
		} catch (IOException e) {
		}
	}
	*/
}
