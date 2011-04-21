package edu.wisc.cs707.src;

import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.ListIterator;
import java.util.Vector;

public class PointsOfInterest implements  List<PointOfInterest> {

	private Vector<PointOfInterest> container = new Vector<PointOfInterest>();
	
	public PointsOfInterest() {
		this.add(new PointOfInterest(-1, "<New Location>", 0, 0, 0, false));
	}
	
	public PointOfInterest get(String name) {
		for (PointOfInterest poi : this.container) {
			if (poi.getName() == name) {
				return poi;
			}
		}
		
		return null;
	}
	
	public PointOfInterest get(double latitude, double longitude) {
		return this.get(latitude, longitude, 0);
	}
	
	public PointOfInterest get(double latitude, double longitude, int accuracy) {
		PointOfInterest p = null;
		
		for (PointOfInterest poi : this.container) {
			if (poi.getId() > 0 && poi.isMonitored() &&
					poi.contains(latitude, longitude, accuracy) && 
					(p == null || p.getRadius() > poi.getRadius())) {
				p = poi;
			}
		}
		
		return null;
	}

	@Override
	public boolean add(PointOfInterest object) {
		return this.container.add(object);		
	}

	@Override
	public void add(int location, PointOfInterest object) {
		this.container.add(location, object);		
	}

	@Override
	public boolean addAll(Collection<? extends PointOfInterest> arg0) {
		return this.container.addAll(arg0);
	}

	@Override
	public boolean addAll(int arg0, Collection<? extends PointOfInterest> arg1) {
		return this.container.addAll(arg0, arg1);
	}

	@Override
	public void clear() {
		this.container.clear();
	}

	@Override
	public boolean contains(Object object) {
		return this.container.contains(object);
	}

	@Override
	public boolean containsAll(Collection<?> arg0) {
		return this.container.containsAll(arg0);
	}

	@Override
	public PointOfInterest get(int location) {
		return this.container.get(location);
	}

	@Override
	public int indexOf(Object object) {
		return this.container.indexOf(object);
	}

	@Override
	public boolean isEmpty() {
		return this.container.isEmpty();
	}

	@Override
	public Iterator<PointOfInterest> iterator() {
		return this.container.iterator();
	}

	@Override
	public int lastIndexOf(Object object) {
		return this.container.lastIndexOf(object);
	}

	@Override
	public ListIterator<PointOfInterest> listIterator() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public ListIterator<PointOfInterest> listIterator(int location) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public PointOfInterest remove(int location) {
		return this.container.remove(location);
	}

	@Override
	public boolean remove(Object object) {
		return this.container.remove(object);
	}

	@Override
	public boolean removeAll(Collection<?> arg0) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public boolean retainAll(Collection<?> arg0) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public PointOfInterest set(int location, PointOfInterest object) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public int size() {
		return this.container.size();
	}

	@Override
	public List<PointOfInterest> subList(int start, int end) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Object[] toArray() {
		int i = 0;
		PointOfInterest [] locations = new PointOfInterest[this.container.size()];
		for (PointOfInterest p : this.container) {
			locations[i++] = p;
		}
		
		return locations;
	}

	@Override
	public <T> T[] toArray(T[] array) {
		// TODO Auto-generated method stub
		return null;
	}
}
