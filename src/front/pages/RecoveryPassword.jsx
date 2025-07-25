import { Link } from "react-router-dom";
import { useState} from "react";

export const RecoveryPassword =() =>{

    const [email, setEmail] = useState("")

    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (event) => {
        event.preventDefault()

        if (!email){
            alert("Por favor ingrese un correo valido")
            return
        }

        const urlbackend = import.meta.env.VITE_BACKEND_URL;
        
        const response = await fetch(`${urlbackend}/api/reset-password`, {
            method: "POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify(email)
        })
        if (response.ok) {
            alert("Link de restauración de contraseña enviado exitosamente")
        }

        setIsLoading(true);
        setTimeout(() => {
            setIsLoading(false);
            alert('Recuperar contraseña');
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

                                <h2 className="h5 text-center text-dark mb-4">Recuperar Contraseña</h2>

                                <form onSubmit={handleSubmit}>
                                    {/* Correo */}
                                    <div className="mb-3">
                                        <label htmlFor="emailInput" className="form-label">Correo electrónico</label>
                                        <div className="input-group">
                                            <span className="input-group-text">
                                                <i className="fas fa-envelope text-secondary"></i>
                                            </span>
                                            <input
                                                type="email"
                                                className="form-control"
                                                id="emailInput"
                                                placeholder="Ingresa tu correo"
                                                name="email"
                                                value={email}
                                                onChange={(event) => setEmail(event.target.value)}
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