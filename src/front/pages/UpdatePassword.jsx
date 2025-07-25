import { useSearchParams, Link, useNavigate } from "react-router-dom";
import { useState } from "react";


export const UpdatePassword = () => {

    const [newPass, setNewPass] = useState()

    const [isLoading, setIsLoading] = useState(false);

    const navigate = useNavigate()

    const [searchParams, _ ] = useSearchParams()

    const handleSubmit = async (event) => {
        event.preventDefault()

        if (!email){
            alert("Por favor ingrese un correo valido")
            return
        }

        const urlbackend = import.meta.env.VITE_BACKEND_URL;
        
        const response = await fetch(`${urlbackend}/api/update-password`, {
            method: "PUT",
            headers:{
                "Authorization": `Bearer ${searchParams.get("token")}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(newPass)
        })

        if (response.ok) {
            navigate("/login")
        }

        setIsLoading(true);
        setTimeout(() => {
            setIsLoading(false);
            alert('Actualizar contraseña');
        }, 2000);
    };
    
    return (
        <div className="min-vh-100 d-flex align-items-center bg-light">
            <div className="container py-5">
                <div className="row justify-content-center">
                    <div className="col-md-6 col-lg-5">
                        <div className="card shadow-sm border-0 rounded-4">
                            <div className="card-body p-4">
                                {/* Logo y título */}
                                <div className="text-center mb-4">
                                    <i className="fas fa-leaf fa-2x text-success mb-2"></i>
                                    <h1 className="h4 fw-bold text-dark">AgriVision AI</h1>
                                </div>

                                <h2 className="h5 text-center text-dark mb-4">Actualizar Contraseña</h2>

                                <form onSubmit={handleSubmit}>
                                    {/* Correo */}
                                    <div className="mb-3">
                                        <label htmlFor="newPassword" className="form-label">Contraseña</label>
                                        <div className="input-group">
                                            <span className="input-group-text">
                                                <i className="fas fa-envelope text-secondary"></i>
                                            </span>
                                            <input
                                                type="text"
                                                className="form-control"
                                                placeholder="contraseña"
                                                id="newPassword"
                                                name="password"
                                                onChange={(event) => setNewPass(event.target.value)}
                                                value={newPass}
                                                required
                                            />
                                        </div>
                                        <div className="invalid-feedback">
                                            Este campo es obligatorio.
                                        </div>
                                    </div>

                                    {/* Botón */}
                                    <button
                                        type="submit"
                                        className="btn btn-success w-100"
                                        disabled={isLoading}
                                    >
                                        {isLoading ? 'Enviando link...' : 'Enviar link'}
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};