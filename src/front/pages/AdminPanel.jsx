import React, { useState, useEffect } from "react";
import useGlobalReducer from "../hooks/useGlobalReducer";

export const AdminPanel = () => {
    const { store } = useGlobalReducer();

    // Estados para administrador
    const [adminView, setAdminView] = useState("overview");
    const [allUsers, setAllUsers] = useState([]);
    const [allFarms, setAllFarms] = useState([]);
    const [selectedAdminFarm, setSelectedAdminFarm] = useState(null);
    const [adminFarmDetails, setAdminFarmDetails] = useState(null);
    const [adminOverview, setAdminOverview] = useState(null);
    const [selectedDiagnosticFile, setSelectedDiagnosticFile] = useState(null);
    const [loading, setLoading] = useState(false);

    // ============ FUNCIONES FETCH ============

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

    // ============ EFECTOS ============

    useEffect(() => {
        fetchAdminOverview();
    }, []);

    // ============ RENDER ============

    return (
        <div className="min-vh-100 bg-light">
            <div className="container py-5">
                <h1 className="text-center text-dark fw-bold mb-4">
                    <i className="fa-solid fa-user-tie me-2"></i>
                    Panel de Administración
                </h1>

                <div className="p-4 bg-white shadow rounded-4">
                    {/* Tabs de navegación */}
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

                    {/* VISTA GENERAL / OVERVIEW */}
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

                    {/* VISTA DE USUARIOS */}
                    {adminView === "users" && (
                        <div>
                            <h5 className="mb-3">👥 Todos los Usuarios</h5>
                            <div className="row">
                                {allUsers.map(user => (
                                    <div key={user.user_id} className="col-md-6 mb-3">
                                        <div className="card">
                                            <div className="card-body">
                                                <div className="d-flex align-items-center mb-3">
                                                    {user.avatar && (
                                                        <img
                                                            src={user.avatar}
                                                            alt="avatar"
                                                            className="rounded-circle me-3"
                                                            style={{ width: "60px", height: "60px", objectFit: "cover" }}
                                                        />
                                                    )}
                                                    <div>
                                                        <h6 className="mb-0">{user.full_name}</h6>
                                                        <small className="text-muted">{user.email}</small>
                                                        {user.is_admin && (
                                                            <span className="badge bg-primary ms-2">Admin</span>
                                                        )}
                                                    </div>
                                                </div>
                                                <p className="mb-2">
                                                    📱 {user.phone_number}<br />
                                                    🌾 {user.farms_count} campo(s)<br />
                                                    📄 {user.total_reports} reporte(s)<br />
                                                    🖼️ {user.total_images} imagen(es)
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* VISTA DE CAMPOS */}
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

                    {/* DETALLES DEL CAMPO SELECCIONADO */}
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
                                                        
                                                            href={report.file_url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="btn btn-sm btn-outline-primary mt-1"
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
                                                        
                                                            href={diagnostic.file_url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="btn btn-sm btn-outline-success mt-1"
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

                            {/* Imágenes del campo */}
                            <div className="card mt-4">
                                <div className="card-header">
                                    <h6>🖼️ Imágenes del Campo</h6>
                                </div>
                                <div className="card-body">
                                    <div className="row">
                                        {adminFarmDetails.images.length === 0 ? (
                                            <p className="text-muted">No hay imágenes</p>
                                        ) : (
                                            adminFarmDetails.images.map(image => (
                                                <div key={image.id} className="col-md-3 mb-3">
                                                    <div className="card">
                                                        <img
                                                            src={image.image_url}
                                                            alt={image.image_type}
                                                            className="card-img-top"
                                                            style={{ height: "150px", objectFit: "cover" }}
                                                        />
                                                        <div className="card-body p-2">
                                                            <small className="text-muted d-block">{image.image_type}</small>
                                                            <small className="text-muted">
                                                                {new Date(image.upload_date).toLocaleDateString()}
                                                            </small>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};