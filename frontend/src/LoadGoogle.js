export const loadGoogleMapsAPI = (apiKey, libraries = []) => {
    return new Promise((resolve, reject) => {
      if (window.google && window.google.maps) {
        resolve(window.google);
        return;
      }
      const script = document.createElement("script");
      const librariesParam = libraries.length ? `&libraries=${libraries.join(",")}` : "";
      script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}${librariesParam}`;
      script.async = true;
      script.defer = true;
      script.onload = () => resolve(window.google);
      script.onerror = () => reject(new Error("Failed to load Google Maps API"));
      document.head.appendChild(script);
    });
  };

  