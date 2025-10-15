'use client';
import React, { useCallback } from 'react';
import { GoogleMap, MarkerF, useJsApiLoader } from '@react-google-maps/api';

const containerStyle = { width: '100%', height: '420px' };

export default function LiveMap({ center, markers = [] }: { center: { lat:number; lng:number }, markers?: { id:any; lat:number; lng:number; label?:string }[] }) {
  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '';
  const { isLoaded, loadError } = useJsApiLoader({ googleMapsApiKey: apiKey });

interface Marker {
    id: any;
    lat: number;
    lng: number;
    label?: string;
}

interface LiveMapProps {
    center: { lat: number; lng: number };
    markers?: Marker[];
}

const onLoad = useCallback((map: google.maps.Map) => { /* configure map if needed */ }, []);

  if (loadError) return <div className="p-4 bg-yellow-50 rounded">Map error: check API key / billing</div>;
  if (!isLoaded) return <div className="p-4">Loading map…</div>;

  return (
    <div className="rounded overflow-hidden shadow">
      <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={14} onLoad={onLoad}>
        {markers.map(m => <MarkerF key={m.id} position={{ lat: m.lat, lng: m.lng }} label={m.label} />)}
      </GoogleMap>
    </div>
  );
}
