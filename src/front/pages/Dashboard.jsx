import React, { useState, useEffect } from "react";
import { Navbar } from "../components/Navbar";
import useGlobalReducer from "../hooks/useGlobalReducer";


export const Dashboard = ({ selectedFarmId }) => {

    const { store, dispatch } = useGlobalReducer();

    // Estados para imágenes
    const [ndviImages, setNdviImages] = useState([]);
    const [aerialImages, setAerialImages] = useState([]);
    const [selectedType, setSelectedType] = useState("ndvi");

    // Estados para farms
    const [selectedFarm, setSelectedFarm] = useState("");
    const [userFarms, setUserFarms] = useState([]);

    // Estados para reportes - CONSOLIDADOS
    const [reports, setReports] = useState([]);
    const [selectedReportFile, setSelectedReportFile] = useState(null);
    const [selectedImageFile, setSelectedImageFile] = useState(null);
    const [diagnosticReports, setDiagnosticReports] = useState([]);         // para diagnósticos del admin
    const [loading, setLoading] = useState(false);
    const [selectedDiagnosticFile, setSelectedDiagnosticFile] = useState(null);

    // Estados para usuario
    const [userRole, setUserRole] = useState("user");       // "user" o "admin"

    // Estados para administrador
    const [adminView, setAdminView] = useState("overview");
    const [allUsers, setAllUsers] = useState([]);
    const [allFarms, setAllFarms] = useState([]);
    const [selectedAdminFarm, setSelectedAdminFarm] = useState(null);
    const [adminFarmDetails, setAdminFarmDetails] = useState(null);
    const [adminOverview, setAdminOverview] = useState(null);

    const getDashboard = async () => {
        const urlBackend = import.meta.env.VITE_BACKEND_URL;
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
                alert("Error al obtener la información: " + (data?.message || response.statusText));
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Error de comunicación con el servidor");
        }
    };


    // Función para obtener el perfil y determinar si es admin
    const fetchUserProfile = async () => {
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

            setUserRole(data.is_admin ? "admin" : "user");

            if (data.farms?.length > 0) {
                setSelectedFarm(data.farms[0].id);
            }
        } catch (error) {
            console.error("Error al obtener perfil:", error);
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
                setSelectedFarm(data.farms[0].id);
            }
        } catch (error) {
            console.error("Error al obtener huertos:", error);
        }
    };

    // ============ FUNCIONES DE REPORTES DE USUARIOS ============

    const fetchReports = async () => {
        const farmId = selectedFarmId || selectedFarm;

        if (!farmId) {
            console.log("No hay huerto seleccionado para obtener reportes");
            setReports([]);
            return;
        }

        const token = store.token;
        const urlBackend = import.meta.env.VITE_BACKEND_URL;

        try {
            const response = await fetch(`${urlBackend}/api/reports?farm_id=${farmId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            const data = await response.json();

            if (response.ok) {
                setReports(data);
            } else {
                console.error("Error al obtener reportes:", data.error);
                setReports([]);
            }
        } catch (error) {
            console.error("Error al obtener reportes:", error);
            setReports([]);
        }
    };

    const fetchUserDiagnostics = async () => {
        const farmId = selectedFarmId || selectedFarm;

        if (!farmId) {
            setDiagnosticReports([]);
            return;
        }

        const token = store.token;
        const urlBackend = import.meta.env.VITE_BACKEND_URL;

        try {
            // Usar el endpoint que obtiene diagnósticos de un campo específico
            const response = await fetch(`${urlBackend}/api/admin/diagnostics/${farmId}`, {
                method: "GET",
                credentials: "include",
                headers: {
                    'Authorization': `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            if (response.ok) {
                const data = await response.json();
                setDiagnosticReports(data.diagnostics || []);
            } else if (response.status === 404) {
                // No hay diagnósticos para este campo
                setDiagnosticReports([]);
            } else {
                console.error("Error al obtener diagnósticos:", response.status);
                setDiagnosticReports([]);
            }

        } catch (error) {
            console.error("Error al obtener diagnósticos:", error);
            setDiagnosticReports([]);
        }
    };


    const handleUploadReport = async () => {
        if (!selectedReportFile) {
            alert("Selecciona un archivo primero");
            return;
        }

        const farmId = selectedFarmId || selectedFarm;

        if (!farmId) {
            alert("Selecciona un campo para subir el reporte");
            return;
        }

        const formData = new FormData();
        formData.append("file_url", selectedReportFile);
        formData.append("farm_id", farmId);

        setLoading(true);

        try {
            const token = store.token;
            const urlBackend = import.meta.env.VITE_BACKEND_URL;

            const response = await fetch(`${urlBackend}/api/upload-report`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                alert("Reporte subido correctamente");
                setSelectedReportFile(null);
                fetchReports();                 // Actualizar la lista de reportes
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            console.error("Error subiendo reporte:", error);
            alert("Error al subir el reporte");
        } finally {
            setLoading(false);
        }
    }

    // ============ FUNCIONES PARA DIAGNÓSTICOS (ADMIN) ============

    const fetchDiagnosticReports = async () => {
        const farmId = selectedFarmId || selectedFarm;

        if (!farmId) {
            setDiagnosticReports([]);
            return;
        }

        const token = store.token;
        const urlBackend = import.meta.env.VITE_BACKEND_URL;

        try {
            // Usar el endpoint específico para un farm
            const response = await fetch(`${urlBackend}/api/get-report/${farmId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            const data = await response.json();

            if (response.ok) {
                setDiagnosticReports([data]);
            } else {
                console.error("Error al obtener diagnósticos:", data.error);
                setDiagnosticReports([]);
            }
        } catch (error) {
            console.error("Error al obtener diagnósticos:", error);
            setDiagnosticReports([]);
        }
    };

    const handleUploadDiagnostic = async () => {
        if (!selectedDiagnosticFile) {
            alert("Selecciona un archivo de diagnóstico primero");
            return;
        }

        const farmId = selectedFarmId || selectedFarm;

        if (!farmId) {
            alert("Selecciona un campo para subir el diagnóstico");
            return;
        }

        const formData = new FormData();
        formData.append("file_url", selectedDiagnosticFile);
        formData.append("farm_id", farmId);

        setLoading(true);

        try {
            const token = store.token;
            const urlBackend = import.meta.env.VITE_BACKEND_URL;

            const response = await fetch(`${urlBackend}/api/upload-report`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                alert("Diagnóstico subido correctamente");
                setSelectedDiagnosticFile(null);
                fetchDiagnosticReports();
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            console.error("Error subiendo diagnóstico:", error);
            alert("Error al subir el diagnóstico");
        } finally {
            setLoading(false);
        }
    };

    const fetchAdminOverview = async () => {
        const token = store.token;
        const urlBackend = import.meta.env.VITE_BACKEND_URL;

        try {
            const response = await fetch(`${urlBackend}/api/admin/reports-overview`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setAdminOverview(data);
            }
        } catch (error) {
            console.error("Error al obtener overview admin:", error);
        }
    };

    const fetchAllUsersAdmin = async () => {
        const token = store.token;
        const urlBackend = import.meta.env.VITE_BACKEND_URL;

        try {
            const response = await fetch(`${urlBackend}/api/admin/all-users`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setAllUsers(data.users);
            }
        } catch (error) {
            console.error("Error al obtener usuarios:", error);
        }
    };

    const fetchAllFarmsAdmin = async () => {
        const token = store.token;
        const urlBackend = import.meta.env.VITE_BACKEND_URL;

        try {
            const response = await fetch(`${urlBackend}/api/admin/all-farms`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setAllFarms(data.farms);
            }
        } catch (error) {
            console.error("Error al obtener campos:", error);
        }
    };

    const fetchAdminFarmDetails = async (farmId) => {
        const token = store.token;
        const urlBackend = import.meta.env.VITE_BACKEND_URL;

        try {
            const response = await fetch(`${urlBackend}/api/admin/farm-details/${farmId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setAdminFarmDetails(data);
            }
        } catch (error) {
            console.error("Error al obtener detalles del campo:", error);
        }
    };

    const handleUploadAdminDiagnostic = async (farmId) => {
        if (!selectedDiagnosticFile) {
            alert("Selecciona un archivo de diagnóstico");
            return;
        }

        const formData = new FormData();
        formData.append("diagnostic_file", selectedDiagnosticFile);
        formData.append("farm_id", farmId);
        formData.append("description", "Diagnóstico profesional realizado por administrador");

        setLoading(true);

        try {
            const token = store.token;
            const urlBackend = import.meta.env.VITE_BACKEND_URL;

            const response = await fetch(`${urlBackend}/api/admin/upload-diagnostic`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                alert("Diagnóstico subido correctamente");
                setSelectedDiagnosticFile(null);

                // Recargar detalles
                if (selectedAdminFarm) {
                    fetchAdminFarmDetails(selectedAdminFarm);
                }
                fetchAdminOverview();
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            console.error("Error subiendo diagnóstico:", error);
            alert("Error al subir el diagnóstico");
        } finally {
            setLoading(false);
        }
    };

    // ============ FUNCIONES DE IMÁGENES ============

    const handleUploadImage = async () => {
        const token = store.token;
        const urlBackend = import.meta.env.VITE_BACKEND_URL;

        if (!selectedImageFile || !selectedFarm) {
            alert("Debes seleccionar una imagen y un campo");
            return;
        }

        const formData = new FormData();
        formData.append("image_type", selectedType.toUpperCase());
        formData.append("image_url", selectedImageFile);
        formData.append("farm_id", selectedFarm);

        try {
            const response = await fetch(`${urlBackend}/api/upload-image`, {
                method: "POST",
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                alert("Imagen subida correctamente");
                setSelectedImageFile(null);
                fetchImages(selectedFarm);      // Recargar imágenes del huerto específico
            } else {
                alert("Error: " + data.error);
            }
        } catch (error) {
            alert("Error al subir la imagen");
            console.error(error);
        }
    };


    // Función para obtener imágenes filtradas por farm
    const fetchImages = async (farmId = null) => {
        const token = store.token;
        const urlBackend = import.meta.env.VITE_BACKEND_URL;

        // Si no se pasa farmId, usar el seleccionado actualmente
        const targetFarmId = farmId || selectedFarmId || selectedFarm;

        if (!targetFarmId) {
            // Si no hay farm seleccionada, limpiar las imágenes
            setNdviImages([]);
            setAerialImages([]);
            return;
        }

        try {
            // CAMBIO: Usar endpoint específico para una farm
            const response = await fetch(`${urlBackend}/api/user-images/${targetFarmId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            if (!response.ok) {
                const text = await response.text();
                console.error("Respuesta errónea:", text);
                throw new Error(`Error del servidor: ${response.status}`);
            }

            const data = await response.json();

            // Filtrar las imágenes por tipo
            const ndvi = data.filter(image => image.image_type === 'NDVI');
            const aerial = data.filter(image => image.image_type === 'AERIAL');

            setNdviImages(ndvi);
            setAerialImages(aerial);

        } catch (error) {
            console.error("Error al cargar imágenes:", error);
            // Si hay error, limpiar las imágenes
            setNdviImages([]);
            setAerialImages([]);
        }
    };

    // ============ EFECTOS ============

    useEffect(() => {
        getDashboard();
        fetchUserProfile();
    }, []);

    useEffect(() => {
        if (userRole === "admin") {
            fetchAdminOverview();
        }
    }, [userRole]);


    // Cargar datos cuando cambie la farm seleccionada
    useEffect(() => {
        const farmId = selectedFarmId || selectedFarm;
        if (farmId) {
            fetchImages(farmId);
            fetchReports();
            fetchDiagnosticReports();
            fetchUserDiagnostics();
        }
    }, [selectedFarmId, selectedFarm]);

    // ============ HANDLERS DE ARCHIVOS ============

    const handleReportFileChange = (event) => {
        setSelectedReportFile(event.target.files[0]);
    };

    const handleImageFileChange = (event) => {
        setSelectedImageFile(event.target.files[0]);
    };

    const handleDiagnosticFileChange = (event) => {
        setSelectedDiagnosticFile(event.target.files[0]);
    };

    // NUEVA: Handler para cambio de farm
    const handleFarmChange = (event) => {
        const newFarmId = event.target.value;
        setSelectedFarm(newFarmId);

        // Limpiar estados al cambiar de farm
        setNdviImages([]);
        setAerialImages([]);
        setReports([]);
        setDiagnosticReports([]);
    };

    return (
        <div className="min-vh-100 bg-light">
            <div className="container py-5">
                <h1 className="text-center text-dark fw-bold mb-4">
                    Dashboard {userRole === "admin" && <span className="">Administrador</span>}
                </h1>

                <div className="mx-auto p-4 text-start bg-white shadow rounded-4">
                    <div className="col-md-12 mb-2">
                        <p className="fs-5 text-secondary">
                            {store.dashboard || "Bienvenido a tu dashboard de Agrovision IA! Acá podrás ver el análisis del historial de tu huerto, y reportes e imagenes guardadas."}
                        </p>
                    </div>
                </div>

                {/* Selector de campo  */}
                <div className="mt-4 p-3 bg-info bg-opacity-10 border border-info rounded-3">
                    <h5 className="mb-2">
                        <i className="fas fa-map-marker-alt me-2"></i>
                        Campo Seleccionado
                    </h5>
                    <select
                        className="form-select border-info"
                        value={selectedFarm}
                        onChange={handleFarmChange}
                    >
                        <option value="">-- Selecciona un campo --</option>
                        {userFarms.map((farm) => (
                            <option key={farm.id} value={farm.id}>
                                {farm.farm_name} - {farm.farm_location}
                            </option>
                        ))}
                    </select>
                    {selectedFarm && (
                        <small className="text-body-secondary">
                            Las imágenes y reportes se filtrarán por este campo
                        </small>
                    )}
                </div>

                {/* Sección de subida de imágenes - Para usuarios */}
                <div className="mt-5 p-4 bg-white shadow rounded-4">
                    <div className="d-flex align-content-center">
                        <i className="fs-4 mt-3 pt-1 fa-solid fa-cloud-arrow-up" style={{ color: "#3fabfd" }}></i>
                        <h4 className="m-3">Subir Imagen NDVI o Aérea</h4>
                    </div>

                    <p className="mb-3 fw-bold">
                        Sube una imagen para poder realizar el análisis detallado del cultivo
                    </p>

                    <label className="form-label fw-bold">Tipo de Imagen:</label>
                    <select
                        className="form-select border-primary mb-2"
                        value={selectedType}
                        onChange={(event) => setSelectedType(event.target.value)}
                    >
                        <option value="ndvi">NDVI</option>
                        <option value="aerial">Aérea</option>
                    </select>

                    <input
                        type="file"
                        accept="image/*"
                        className="form-control border-primary mb-2"
                        onChange={handleImageFileChange}
                    />
                    <button
                        className="btn btn-success mt-2 w-25"
                        onClick={handleUploadImage}
                        disabled={!selectedImageFile || !selectedFarm}
                    >
                        Subir Imagen
                    </button>
                </div>

                {/* Sección de reportes de usuarios */}
                <div className="mt-5 p-4 bg-white shadow rounded-4">
                    <div className="d-flex align-content-center">
                        <i className="fs-4 mt-3 pt-1 fa-solid fa-file-text" style={{ color: "#28a745" }}></i>
                        <h4 className="m-3">Mis Informes de Campo</h4>
                    </div>

                    <p className="mb-3">
                        Sube informes adicionales de tu campo para ser considerados en el diagnóstico
                    </p>

                    {/* Subir reporte de usuario */}
                    <div className="mb-4">
                        <label className="form-label fw-bold">Subir nuevo informe:</label>
                        <input
                            type="file"
                            accept=".pdf,.doc,.docx,.txt"
                            className="form-control border-success mb-2"
                            onChange={handleReportFileChange}
                        />
                        <button
                            className="btn btn-success mt-2 w-25"
                            onClick={handleUploadReport}
                            disabled={loading || !selectedReportFile || !selectedFarm}
                        >
                            {loading ? "Subiendo..." : "Subir Informe"}
                        </button>
                    </div>

                    {/* Mostrar reportes de usuario */}
                    <div>
                        <h5 className="mb-3">Mis informes subidos:</h5>
                        {reports.length === 0 ? (
                            <p className="text-muted">No has subido informes aún para este campo</p>
                        ) : (
                            <div className="row">
                                {reports.map(report => (
                                    <div key={report.id} className="col-md-6 mb-3">
                                        <div className="card border-success">
                                            <div className="card-body">
                                                <h6 className="card-title">{report.file_name}</h6>
                                                <p className="card-text text-muted">
                                                    Subido: {new Date(report.uploaded_at).toLocaleDateString()}
                                                </p>
                                                <a
                                                    href={report.file_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="btn btn-success btn-sm"
                                                >
                                                    Ver / Descargar
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Diagnósticos del Administrador */}
                <div className="mt-5 p-4 bg-white shadow rounded-4">
                    <div className="d-flex align-content-center">
                        <i className="fs-4 mt-3 pt-1 fa-solid fa-user-md" style={{ color: "#dc3545" }}></i>
                        <h4 className="m-3">Informes de Diagnóstico</h4>
                    </div>

                    {userRole === "admin" && (
                        <div className="mb-4 p-3 bg-warning bg-opacity-10 border border-warning rounded">
                            <h5>Panel de Administrador</h5>
                            <p>Como administrador, puedes subir diagnósticos basados en las imágenes e informes de los usuarios</p>

                            <label className="form-label fw-bold">Subir diagnóstico:</label>
                            <input
                                type="file"
                                accept=".pdf,.doc,.docx,.txt"
                                className="form-control border-warning mb-2"
                                onChange={handleDiagnosticFileChange}
                            />
                            <button
                                className="btn btn-warning mt-2 w-25"
                                onClick={handleUploadDiagnostic}
                                disabled={loading || !selectedDiagnosticFile || !selectedFarm}
                            >
                                {loading ? "Subiendo..." : "Subir Diagnóstico"}
                            </button>
                        </div>
                    )}

                    {/* Mostrar diagnósticos disponibles */}
                    <div>
                        <h5 className="mb-3">Diagnósticos disponibles:</h5>
                        {diagnosticReports.length === 0 ? (
                            <p className="text-muted">
                                {userRole === "admin"
                                    ? "No hay diagnósticos aún para este campo"
                                    : "El administrador aún no ha subido diagnósticos para este campo"
                                }
                            </p>
                        ) : (
                            <div className="row">
                                {diagnosticReports.map(report => (
                                    <div key={report.id} className="col-md-6 mb-3">
                                        <div className="card border-danger">
                                            <div className="card-body">
                                                <h6 className="card-title">
                                                    <i className="fas fa-stethoscope me-2"></i>
                                                    {report.file_name}
                                                </h6>
                                                <p className="card-text text-muted">
                                                    Diagnóstico realizado: {new Date(report.uploaded_at).toLocaleDateString()}
                                                </p>
                                                <p className="card-text">
                                                    <small className="text-muted">
                                                        {report.description || "Diagnóstico profesional del campo"}
                                                    </small>
                                                </p>
                                                <a
                                                    href={report.file_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="btn btn-danger btn-sm"
                                                >
                                                    <i className="fas fa-download me-1"></i>
                                                    Ver Diagnóstico
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* SECCIÓN DE ADMINISTRACIÓN */}
                {userRole === "admin" && (
                    <div className="mt-5 p-4 bg-warning bg-opacity-10 border border-warning rounded-4">
                        <div className="d-flex align-items-center mb-4">
                            <i className="fa-solid fa-user-tie fs-3 text-primary me-3"></i>
                            <h3 className="mb-0">Panel de Administración</h3>
                        </div>

                        {/* Tabs de administración */}
                        <ul className="nav nav-pills mb-4">
                            <li className="nav-item">
                                <button
                                    className={`nav-link ${adminView === "overview" ? "active" : ""}`}
                                    onClick={() => {
                                        setAdminView("overview");
                                        fetchAdminOverview();
                                    }}
                                >
                                    📊 Vista General
                                </button>
                            </li>
                            <li className="nav-item">
                                <button
                                    className={`nav-link ${adminView === "users" ? "active" : ""}`}
                                    onClick={() => {
                                        setAdminView("users");
                                        fetchAllUsersAdmin();
                                    }}
                                >
                                    👥 Usuarios
                                </button>
                            </li>
                            <li className="nav-item">
                                <button
                                    className={`nav-link ${adminView === "farms" ? "active" : ""}`}
                                    onClick={() => {
                                        setAdminView("farms");
                                        fetchAllFarmsAdmin();
                                    }}
                                >
                                    🌾 Gestionar Campos
                                </button>
                            </li>
                        </ul>

                        {/* Contenido del Overview */}
                        {adminView === "overview" && adminOverview && (
                            <div>
                                <h5 className="mb-3">📊 Estadísticas del Sistema</h5>

                                <div className="row mb-4">
                                    <div className="col-md-3">
                                        <div className="card text-center border-primary">
                                            <div className="card-body">
                                                <h4 className="text-primary">{adminOverview.overview.total_users}</h4>
                                                <p className="mb-0">👤 Usuarios</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="col-md-3">
                                        <div className="card text-center border-info">
                                            <div className="card-body">
                                                <h4 className="text-info">{adminOverview.overview.total_farms}</h4>
                                                <p className="mb-0">🌾 Campos</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="col-md-3">
                                        <div className="card text-center border-warning">
                                            <div className="card-body">
                                                <h4 className="text-warning">{adminOverview.overview.total_user_reports}</h4>
                                                <p className="mb-0">📄 Reportes Pendientes</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="col-md-3">
                                        <div className="card text-center border-success">
                                            <div className="card-body">
                                                <h4 className="text-success">{adminOverview.overview.total_admin_diagnostics}</h4>
                                                <p className="mb-0">✅ Diagnósticos</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Campos que necesitan atención */}
                                <div className="card border-warning">
                                    <div className="card-header bg-warning">
                                        <h6 className="mb-0 text-dark">🚨 Campos que necesitan diagnóstico</h6>
                                    </div>
                                    <div className="card-body">
                                        {adminOverview.farms_needing_attention.length === 0 ? (
                                            <p className="text-success mb-0">🎉 Todos los campos tienen diagnósticos</p>
                                        ) : (
                                            <div className="row">
                                                {adminOverview.farms_needing_attention.map(farm => (
                                                    <div key={farm.farm_id} className="col-md-6 mb-2">
                                                        <div className="border rounded p-3 bg-light">
                                                            <strong>{farm.farm_name}</strong><br />
                                                            <span>📍 {farm.farm_location}</span><br />
                                                            <span>👤 {farm.owner}</span><br />
                                                            <span className="text-warning">📄 {farm.user_reports} reportes sin diagnosticar</span><br />
                                                            <button
                                                                className="btn btn-warning btn-sm mt-2"
                                                                onClick={() => {
                                                                    setSelectedAdminFarm(farm.farm_id);
                                                                    setAdminView("farm-details");
                                                                    fetchAdminFarmDetails(farm.farm_id);
                                                                }}
                                                            >
                                                                Gestionar
                                                            </button>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Contenido de Campos */}
                        {adminView === "farms" && (
                            <div>
                                <h5 className="mb-3">🌾 Gestión de Campos</h5>
                                <div className="row">
                                    {allFarms.map(farm => (
                                        <div key={farm.farm_id} className="col-md-6 mb-3">
                                            <div className="card">
                                                <div className="card-body">
                                                    <h6 className="card-title">🌾 {farm.farm_name}</h6>
                                                    <p className="mb-2">
                                                        📍 {farm.farm_location}<br />
                                                        👤 {farm.user_name} ({farm.user_email})
                                                    </p>

                                                    <div className="row text-center mb-2">
                                                        <div className="col-3">
                                                            <strong>{farm.statistics.user_reports}</strong><br />
                                                            <small>Informes</small>
                                                        </div>
                                                        <div className="col-3">
                                                            <strong>{farm.statistics.admin_diagnostics}</strong><br />
                                                            <small>Diagnósticos</small>
                                                        </div>
                                                        <div className="col-3">
                                                            <strong>{farm.statistics.ndvi_images}</strong><br />
                                                            <small>NDVI</small>
                                                        </div>
                                                        <div className="col-3">
                                                            <strong>{farm.statistics.aerial_images}</strong><br />
                                                            <small>Aéreas</small>
                                                        </div>
                                                    </div>

                                                    <button
                                                        className="btn btn-primary btn-sm w-100"
                                                        onClick={() => {
                                                            setSelectedAdminFarm(farm.farm_id);
                                                            setAdminView("farm-details");
                                                            fetchAdminFarmDetails(farm.farm_id);
                                                        }}
                                                    >
                                                        Ver detalles y subir diagnóstico
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Detalles del campo seleccionado */}
                        {adminView === "farm-details" && adminFarmDetails && (
                            <div>
                                <div className="d-flex justify-content-between align-items-center mb-3">
                                    <h5>🌾 {adminFarmDetails.farm.farm_name}</h5>
                                    <button
                                        className="btn btn-secondary btn-sm"
                                        onClick={() => setAdminView("farms")}
                                    >
                                        ← Volver
                                    </button>
                                </div>

                                {/* Subir diagnóstico */}
                                <div className="card mb-4 border-success">
                                    <div className="card-header bg-success text-white">
                                        <h6 className="mb-0">📝 Subir Diagnóstico para este Campo</h6>
                                    </div>
                                    <div className="card-body">
                                        <div className="mb-3">
                                            <p><strong>Campo:</strong> {adminFarmDetails.farm.farm_name}</p>
                                            <p><strong>Propietario:</strong> {adminFarmDetails.owner.full_name} ({adminFarmDetails.owner.email})</p>
                                        </div>

                                        <input
                                            type="file"
                                            accept=".pdf,.doc,.docx,.txt"
                                            className="form-control mb-3"
                                            onChange={(e) => setSelectedDiagnosticFile(e.target.files[0])}
                                        />

                                        <button
                                            className="btn btn-success"
                                            onClick={() => handleUploadAdminDiagnostic(adminFarmDetails.farm.id)}
                                            disabled={!selectedDiagnosticFile || loading}
                                        >
                                            {loading ? "Subiendo..." : "Subir Diagnóstico"}
                                        </button>
                                    </div>
                                </div>

                                {/* Reportes y diagnósticos */}
                                <div className="row">
                                    <div className="col-md-6">
                                        <div className="card">
                                            <div className="card-header">
                                                <h6>📄 Reportes del Usuario</h6>
                                            </div>
                                            <div className="card-body">
                                                {adminFarmDetails.user_reports.length === 0 ? (
                                                    <p className="text-muted">No hay reportes</p>
                                                ) : (
                                                    adminFarmDetails.user_reports.map(report => (
                                                        <div key={report.id} className="mb-2 p-2 border-bottom">
                                                            <strong>{report.file_name}</strong><br />
                                                            <small className="text-muted">
                                                                {new Date(report.uploaded_at).toLocaleDateString()}
                                                            </small><br />
                                                            <a
                                                                href={report.file_url}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="btn btn-sm btn-outline-primary"
                                                            >
                                                                Ver
                                                            </a>
                                                        </div>
                                                    ))
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="col-md-6">
                                        <div className="card">
                                            <div className="card-header">
                                                <h6>✅ Mis Diagnósticos</h6>
                                            </div>
                                            <div className="card-body">
                                                {adminFarmDetails.admin_diagnostics.length === 0 ? (
                                                    <p className="text-muted">No hay diagnósticos</p>
                                                ) : (
                                                    adminFarmDetails.admin_diagnostics.map(diagnostic => (
                                                        <div key={diagnostic.id} className="mb-2 p-2 border-bottom">
                                                            <strong>{diagnostic.file_name}</strong><br />
                                                            <small className="text-muted">
                                                                {new Date(diagnostic.uploaded_at).toLocaleDateString()}
                                                            </small><br />
                                                            <a
                                                                href={diagnostic.file_url}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="btn btn-sm btn-outline-success"
                                                            >
                                                                Ver
                                                            </a>
                                                        </div>
                                                    ))
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Mostrar imágenes - mostrar solo del campo seleccionado */}
                <div className="mt-5">
                    <h4>
                        <i className="fas fa-images me-2"></i>
                        Imágenes del Campo
                        {selectedFarm && (
                            <small className="text-muted ms-2">
                                ({userFarms.find(farm => farm.id == selectedFarm)?.farm_name})
                            </small>
                        )}
                    </h4>

                    {!selectedFarm ? (
                        <div className="alert alert-info">
                            <i className="fas fa-info-circle me-2"></i>
                            Selecciona un campo para ver sus imágenes
                        </div>
                    ) : (
                        <>
                            <h5 className="mt-4">Imágenes NDVI</h5>
                            <div className="row">
                                {ndviImages.length === 0 ? (
                                    <p className="text-muted">No hay imágenes NDVI para este campo</p>
                                ) : (
                                    ndviImages.map((image) => (
                                        <div key={image.id} className="col-md-4 mb-3">
                                            <div className="card">
                                                <img src={image.image_url} alt="NDVI" className="card-img-top" style={{ height: "200px", objectFit: "cover" }} />
                                                <div className="card-body">
                                                    <p className="card-text">
                                                        <small className="text-muted">
                                                            {image.upload_date && new Date(image.upload_date).toLocaleDateString()}
                                                        </small>
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>

                            <h5 className="mt-4">Imágenes Aéreas</h5>
                            <div className="row">
                                {aerialImages.length === 0 ? (
                                    <p className="text-muted">No hay imágenes aéreas para este campo</p>
                                ) : (
                                    aerialImages.map((image) => (
                                        <div key={image.id} className="col-md-4 mb-3">
                                            <div className="card">
                                                <img src={image.image_url} alt="Aérea" className="card-img-top" style={{ height: "200px", objectFit: "cover" }} />
                                                <div className="card-body">
                                                    <p className="card-text">
                                                        <small className="text-muted">
                                                            {image.upload_date && new Date(image.upload_date).toLocaleDateString()}
                                                        </small>
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};