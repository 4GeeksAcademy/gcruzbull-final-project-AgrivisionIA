import React, { useState, useEffect } from "react";
import { Navbar } from "../components/Navbar";
import useGlobalReducer from "../hooks/useGlobalReducer";


export const Dashboard = () => {

    const { store, dispatch } = useGlobalReducer();


    const [ndviImages, setNdviImages] = useState([]);
    const [aerialImages, setAerialImages] = useState([]);
    const [images, setImages] = useState([])

    const [selectedFile, setSelectedFile] = useState(null);

    const [selectedType, setSelectedType] = useState("ndvi"); // ndvi o aerial

    const [selectedFarm, setSelectedFarm] = useState("");
    const [userFarms, setUserFarms] = useState([]);

    const getDashboard = async () => {

        const urlBackend = import.meta.env.VITE_BACKEND_URL;
        // const token = localStorage.getItem("token");
        const token = store.token;

        if (!token) {
            alert("Debes iniciar sesión para acceder al dashboard.");
            return;
        }

        try {
            const response = await fetch(`${urlBackend}/api/dashboard`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
            });
            const data = await response.json();

            if (response.ok) {
                dispatch({ type: "set_dashboard", payload: data.message });
            } else {
                console.error("Error del backend:", data);
                alert("Error al obtener la información:" + (data?.message || response.statusText));
            }
        } catch (error) {
            if (error.message) throw new Error(
                `Comuniquese con soporte por favor`
            );
        }
    };


    const fetchImages = async () => {
        const token = store.token;
        const urlBackend = import.meta.env.VITE_BACKEND_URL;

        try {
            const response = await fetch(`${urlBackend}/api/user-images`, {
                headers: {
                    'Authorization':  `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            if (!response.ok) {
                const text = await response.text(); // ← Mostrar qué se devolvió
                console.error("Respuesta inesperada:", text);
                throw new Error(`Error del servidor: ${response.status}`);
            }

            const data = await response.json();

            

            // Filtrar las imágenes por tipo
            const ndvi = data.filter(image => image.image_type === 'NDVI');
            const aerial = data.filter(image => image.image_type === 'AERIAL');

            setNdviImages(ndvi);
            setAerialImages(aerial);
            setSelectedFile(data);

        } catch (error) {
            console.error("Error al cargar imágenes:", error);
        }
    };

    const fetchFarms = async () => {
        const token = store.token;
        const urlBackend = import.meta.env.VITE_BACKEND_URL;

        try {
            const response = await fetch(`${urlBackend}/api/profile`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            const data = await response.json();
            setUserFarms(data.farms || []);
            if (data.farms?.length > 0) {
                setSelectedFarm(data.farms[0].id);  // preselecciona uno
            }
        } catch (error) {
            console.error("Error al obtener huertos:", error);
        }
    };


    // Cargar las imágenes al cargar el componente
    useEffect(() => {
        getDashboard();
        fetchImages();
        fetchFarms();
    }, []);

    // Subir imagen:
    const handleUploadImage = async () => {
        const token = store.token;
        const urlBackend = import.meta.env.VITE_BACKEND_URL;

        if (!selectedFile || !selectedFarm) {
            alert("Debes seleccionar una imagen y un campo");
            return;
        }

        const formData = new FormData();
        formData.append("image_type", selectedType.toUpperCase()); // "NDVI" o "AERIAL"
        formData.append("image_url", selectedFile);
        formData.append("farm_id", selectedFarm);

        try {
            const response = await fetch(`${urlBackend}/api/upload-image`, {
                method: "POST",
                credentials: "include",
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                alert("Imagen subida correctamente");
                setSelectedFile(null);
                fetchImages();
            } else {
                alert("Error: " + data.error);
            }
        } catch (error) {
            alert("Error al subir la imagen");
            console.error(error);
        }
    };


    return (
        <div className="min-vh-100 bg-light">
            <div className="container py-5">
                <div className="mx-auto mb-2 p-1" style={{ maxWidth: "900px" }} >
                    <h1 className="text-center display-6 fw-bold text-dark mb-4">
                        Dashboard
                    </h1>
                </div>

                <div className="mx-auto p-4 text-start bg-white shadow rounded-4">
                    <div className="col-md-12 mb-2">
                        {/* <div> */}
                        <p className="fs-5 text-secondary">
                            {store.dashboard || "Bienvenido a tu dashboard de Agrovision IA! Acá podrás ver el análisis del historial de tu huerto, reportes guardados, y configuraciones de cuenta."}
                        </p>
                        {/* </div> */}
                    </div>
                </div>

                <div className="mt-5 p-4 bg-white shadow rounded-4">
                    <div className="d-flex align-content-center ">
                        <i className="fs-4 mt-3 pt-1 fa-solid fa-cloud-arrow-up" style={{ color: "#3fabfd" }}></i>
                        <h4 className="m-3">Subir Imagen NDVI o Aérea</h4>
                    </div>

                    <p className="mb-3 fw-bold">
                        Sube una imagen para ver el análisis detallado del cultivo
                    </p>

                    <div className="mb-2">
                        <label className="form-label fw-bold">Tipo de Imagen:</label>
                        <select
                            className="form-select border-primary"
                            value={selectedType}
                            onChange={(event) => setSelectedType(event.target.value)}
                        >
                            <option value="ndvi">
                                NDVI
                            </option>
                            <option value="aerial">
                                Aérea
                            </option>
                        </select>
                    </div>

                    <div className="mb-2">
                        <label className="form-label fw-bold">Selecciona un Campo:</label>
                        <select
                            className="form-select border-primary"
                            value={selectedFarm}
                            onChange={(event) => setSelectedFarm(event.target.value)}
                        >
                            {userFarms.map((farm) => (
                                <option key={farm.id} value={farm.id}>
                                    {farm.farm_name} - {farm.farm_location}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="mb-3">
                        <input
                            type="file"
                            className="form-control border-primary"
                            onChange={(event) => setSelectedFile(event.target.files[0])}
                        />
                    </div>

                    <button
                        className="btn btn-primary fw-bold"
                        onClick={handleUploadImage}
                    >
                        Subir Imagen
                    </button>
                </div>

                <div className="mt-5">
                    <h4>NDVI Images</h4>
                    <div className="row">
                        {ndviImages.map((image) => (
                            <div key={image.id} className="col-md-4 mb-3">
                                <img src={image.image_url} alt="NDVI" className="img-fluid rounded" />
                            </div>
                        ))}
                    </div>

                    <h4 className="mt-4">Aerial Images</h4>
                    <div className="row">
                        {aerialImages.map((image) => (
                            <div key={image.id} className="col-md-4 mb-3">
                                <img src={image.image_url} alt="Aérea" className="img-fluid rounded" />
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
};