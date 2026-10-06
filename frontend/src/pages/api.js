import { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

export function useApi(path) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let live = true;
    fetch(`${API}${path}`)
      .then((response) => {
        if (!response.ok) throw Error("The analytics service could not complete this request.");
        return response.json();
      })
      .then((result) => live && setData(Array.isArray(result) ? result : []))
      .catch((requestError) => live && setError(requestError.message))
      .finally(() => live && setLoading(false));
    return () => { live = false; };
  }, [path]);

  return { data, loading, error };
}
