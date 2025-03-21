//
// Created by adada on 20/3/2025.
//

# include "mc_read_load_compute.hpp"


void mc_computation::init_Px_Py_Qx_Qy()
{
    std::string name;

    std::string Px_inFileName, Py_inFileName, Qx_inFileName, Qy_inFileName;
    if (this->flushLastFile == -1)
    {
        name = "init";

        Px_inFileName = out_Px_path + "/Px_" + name + ".pkl";

        Py_inFileName = out_Py_path + "/Py_" + name + ".pkl";

        Qx_inFileName = out_Qx_path + "/Qx_" + name + ".pkl";

        Qy_inFileName = out_Qy_path + "/Qy_" + name + ".pkl";

        this->load_pickle_data(Px_inFileName, Px_init, N0 * N1);
        this->load_pickle_data(Py_inFileName, Py_init, N0 * N1);
        this->load_pickle_data(Qx_inFileName, Qx_init, N0 * N1);
        this->load_pickle_data(Qy_inFileName, Qy_init, N0 * N1);
    } //end flushLastFile==-1
    else
    {
        name="flushEnd"+std::to_string(this->flushLastFile);
        Px_inFileName=out_Px_path+"/"+name+".Px.pkl";

        Py_inFileName=out_Py_path+"/"+name+".Py.pkl";

        Qx_inFileName=out_Qx_path+"/"+name+".Qx.pkl";

        Qy_inFileName=out_Qy_path+"/"+name+".Qy.pkl";

        //load Px
        this->load_pickle_data(Px_inFileName,Px_all_ptr,sweepToWrite * N0 * N1);
        //copy last N0*N1 elements of to Px_init
        std::memcpy(Px_init.get(),Px_all_ptr.get()+N0*N1*(sweepToWrite-1),
            N0*N1*sizeof(double));

        //load Py
        this->load_pickle_data(Py_inFileName,Py_all_ptr,sweepToWrite * N0 * N1);
        //copy last N0*N1 elements of to Py_init
        std::memcpy(Py_init.get(),Py_all_ptr.get()+N0*N1*(sweepToWrite-1),
            N0*N1*sizeof(double));


        //load Qx
        this->load_pickle_data(Qx_inFileName,Qx_all_ptr,sweepToWrite * N0 * N1);
        //copy last N0*N1 elements of to Qx_init
        std::memcpy(Qx_init.get(),Qx_all_ptr.get()+N0*N1*(sweepToWrite-1),
            N0*N1*sizeof(double));

        //load Qy
        this->load_pickle_data(Qy_inFileName,Qy_all_ptr,sweepToWrite * N0 * N1);
        //copy last N0*N1 elements of to Qy_init
        std::memcpy(Qy_init.get(),Qy_all_ptr.get()+N0*N1*(sweepToWrite-1),
            N0*N1*sizeof(double));
    }
}


void mc_computation::load_pickle_data(const std::string& filename, std::shared_ptr<double[]>& data_ptr,
                                      std::size_t size)
{
    // Initialize Python and NumPy
    Py_Initialize();
    np::initialize();


    try
    {
        // Use Python's 'io' module to open the file directly in binary mode
        py::object io_module = py::import("io");
        py::object file = io_module.attr("open")(filename, "rb"); // Open file in binary mode

        // Import the 'pickle' module
        py::object pickle_module = py::import("pickle");

        // Use pickle.load to deserialize from the Python file object
        py::object loaded_data = pickle_module.attr("load")(file);

        // Close the file
        file.attr("close")();

        // Check if the loaded object is a NumPy array
        if (py::extract<np::ndarray>(loaded_data).check())
        {
            np::ndarray np_array = py::extract<np::ndarray>(loaded_data);

            // Convert the NumPy array to a Python list using tolist()
            py::object py_list = np_array.attr("tolist")();

            // Ensure the list size matches the expected size
            ssize_t list_size = py::len(py_list);
            if (static_cast<std::size_t>(list_size) > size)
            {
                throw std::runtime_error("The provided shared_ptr array size is smaller than the list size.");
            }

            // Copy the data from the Python list to the shared_ptr array
            for (ssize_t i = 0; i < list_size; ++i)
            {
                data_ptr[i] = py::extract<double>(py_list[i]);
            }
        }
        else
        {
            throw std::runtime_error("Loaded data is not a NumPy array.");
        }
    }
    catch (py::error_already_set&)
    {
        PyErr_Print();
        throw std::runtime_error("Python error occurred.");
    }
}


void mc_computation::save_array_to_pickle(const std::shared_ptr<double[]>& ptr, int size, const std::string& filename)
{
    using namespace boost::python;
    namespace np = boost::python::numpy;

    // Initialize Python interpreter if not already initialized
    if (!Py_IsInitialized())
    {
        Py_Initialize();
        if (!Py_IsInitialized())
        {
            throw std::runtime_error("Failed to initialize Python interpreter");
        }
        np::initialize(); // Initialize NumPy
    }

    try
    {
        // Import the pickle module
        object pickle = import("pickle");
        object pickle_dumps = pickle.attr("dumps");

        // Convert C++ array to NumPy array using shared_ptr
        np::ndarray numpy_array = np::from_data(
            ptr.get(), // Use shared_ptr's raw pointer
            np::dtype::get_builtin<double>(), // NumPy data type (double)
            boost::python::make_tuple(size), // Shape of the array (1D array)
            boost::python::make_tuple(sizeof(double)), // Strides
            object() // Optional base object
        );

        // Serialize the NumPy array using pickle.dumps
        object serialized_array = pickle_dumps(numpy_array);

        // Extract the serialized data as a string
        std::string serialized_str = extract<std::string>(serialized_array);

        // Write the serialized data to a file
        std::ofstream file(filename, std::ios::binary);
        if (!file)
        {
            throw std::runtime_error("Failed to open file for writing");
        }
        file.write(serialized_str.data(), serialized_str.size());
        file.close();

        // Debug output (optional)
        // std::cout << "Array serialized and written to file successfully." << std::endl;
    }
    catch (const error_already_set&)
    {
        PyErr_Print();
        std::cerr << "Boost.Python error occurred." << std::endl;
    } catch (const std::exception& e)
    {
        std::cerr << "Exception: " << e.what() << std::endl;
    }
}
///
/// @param n0
/// @param n1
/// @return flatenned index
int mc_computation::double_ind_to_flat_ind(const int& n0, const int& n1)
{
    return n0 * N1 + n1;
}

int mc_computation::mod_direction0(const int&m0)
{

return ((m0 % N0) + N0) % N0;

}

int mc_computation::mod_direction1(const int&m1)
{return ((m1 % N1) + N1) % N1;
}

void mc_computation::init_mats()
{
    ////////////////////////////////////////////////////////////////////////
    //init A_T
    arma::sp_dmat A(N0*N1,N0*N1);
    for (int n0=0;n0<N0;n0++)
    {
        for (int n1=0;n1<N1;n1++)
        {
            for (int m0=n0-Nx;m0<n0+Nx+1;m0++)
            {
                for (int m1=n1-Ny;m1<n1+Ny+1;m1++)
                {
                    int flat_ind_row=double_ind_to_flat_ind(n0,n1);
                    int m0_mod=mod_direction0(m0);
                    int m1_mod=mod_direction1(m1);
                    double tmp = std::pow(m0 - n0, 2.0) - (m0 - n0) * (m1 - n1) + std::pow(m1 - n1, 2.0);
                    int flat_ind_col=double_ind_to_flat_ind(m0_mod,m1_mod);
                    if (flat_ind_row==flat_ind_col)
                    {
                        continue;
                    }else
                    {
                        A(flat_ind_row,flat_ind_col)=1.0 / tmp;
                    }//end if else
                }//end m1
            }//end m0
        }//end n1
    }//end n0

    this->A_T=A.t();
    // save and check
    // arma::dmat A_dense(A_T);
    // double* raw_ptr = A_dense.memptr();
    // std::shared_ptr<double[]> sptr(raw_ptr, [](double* p) {
    // /* do nothing */
    // });
    // std::string outA="./A.pkl";
    // this->save_array_to_pickle(sptr,N0*N1*N0*N1,outA);
    //
    //
    // std::cout<<"A saved"<<std::endl;
    //end A_T init
    ////////////////////////////////////////////////////////////////////////
    ///
    ///////////////////////////////////////////////////////////////////////////
    //init B_T
    arma::sp_dmat B(N0*N1,N0*N1);
    for (int n0=0;n0<N0;n0++)
    {
        for (int n1=0;n1<N1;n1++)
        {
            for (int m0=n0-Nx;m0<n0+Nx+1;m0++)
            {
                for (int m1=n1-Ny;m1<n1+Ny+1;m1++)
                {
                    int flat_ind_row=double_ind_to_flat_ind(n0,n1);
                    int m0_mod=mod_direction0(m0);
                    int m1_mod=mod_direction1(m1);
                    int flat_ind_col=double_ind_to_flat_ind(m0_mod,m1_mod);
                    if (flat_ind_row==flat_ind_col)
                    {
                        continue;
                    }else
                    {
                        double up = std::pow(m0 - n0 - 0.5 * m1 + 0.5 * n1, 2.0);
                        double down_tmp = std::pow(m0 - n0, 2.0) - (m0 - n0) * (m1 - n1) + std::pow(m1 - n1, 2.0);
                        double down = std::pow(down_tmp, 2.0);
                        B(flat_ind_row,flat_ind_col)=up / down;
                    }//end if else


                }//end m1
            }//end m0
        }//end n1
    }//end n0

    this->B_T=B.t();
    //save and check
    // arma::dmat B_dense(B_T);
    // double* raw_ptr = B_dense.memptr();
    // std::shared_ptr<double[]> sptr(raw_ptr, [](double* p) {
    // /* do nothing */
    // });
    // std::string outB="./B.pkl";
    // this->save_array_to_pickle(sptr,N0*N1*N0*N1,outB);
    // std::cout<<"B saved"<<std::endl;
    //end init B_T
    ///////////////////////////////////////////////////////////////////////////
    ///
    //////////////////////////////////////////////////////////////////////////////
    /// init C_T
    arma::sp_dmat C(N0*N1,N0*N1);

    ///end init C_T
    for (int n0=0;n0<N0;n0++)
    {
        for (int n1=0;n1<N1;n1++)
        {
            for (int m0=n0-Nx;m0<n0+Nx+1;m0++)
            {
                for (int m1=n1-Ny;m1<n1+Ny+1;m1++)
                {
                    int flat_ind_row=double_ind_to_flat_ind(n0,n1);
                    int m0_mod=mod_direction0(m0);
                    int m1_mod=mod_direction1(m1);
                    int flat_ind_col=double_ind_to_flat_ind(m0_mod,m1_mod);
                    if (flat_ind_row==flat_ind_col)
                    {
                        continue;
                    }else
                    {
                        double up = (m0 - n0 - 0.5 * m1 + 0.5 * n1) * (m1 - n1);
                        double down_tmp = std::pow(m0 - n0, 2.0) - (m0 - n0) * (m1 - n1) + std::pow(m1 - n1, 2.0);
                        double down = std::pow(down_tmp, 2.0);

                        C(flat_ind_row,flat_ind_col)=up / down;

                    }//end if else

                }//end m1
            }//end m0
        }//end n1
    }//end n0
    this->C_T=C.t();
    //save and check
    // arma::dmat C_dense(C_T);
    // double* raw_ptr = C_dense.memptr();
    // std::shared_ptr<double[]> sptr(raw_ptr, [](double* p) {
    // /* do nothing */
    // });
    // std::string outC="./C.pkl";
    // this->save_array_to_pickle(sptr,N0*N1*N0*N1,outC);
    // std::cout<<"C saved"<<std::endl;
    //end init C_T
    //////////////////////////////////////////////////////////////////////////////
    /// init G_T
    arma::sp_dmat G(N0*N1,N0*N1);
    for (int n0=0;n0<N0;n0++)
    {
        for (int n1=0;n1<N1;n1++)
        {
            for (int m0=n0-Nx;m0<n0+Nx+1;m0++)
            {
                for (int m1=n1-Ny;m1<n1+Ny+1;m1++)
                {

                    int flat_ind_row=double_ind_to_flat_ind(n0,n1);
                    int m0_mod=mod_direction0(m0);
                    int m1_mod=mod_direction1(m1);
                    int flat_ind_col=double_ind_to_flat_ind(m0_mod,m1_mod);
                    if (flat_ind_row==flat_ind_col)
                    {
                        continue;
                    }else
                    {
                        double up = std::pow(m1 - n1, 2.0);
                        double down_tmp = std::pow(m0 - n0, 2.0) - (m0 - n0) * (m1 - n1) + std::pow(m1 - n1, 2.0);
                        double down = std::pow(down_tmp, 2.0);
                        G(flat_ind_row,flat_ind_col)=up / down;
                    }//end if else

                }//end m1
            }//end m0
        }//end n1
    }//end n0
    this->G_T=G.t();
    // arma::dmat G_dense(G_T);
    // double* raw_ptr = G_dense.memptr();
    // std::shared_ptr<double[]> sptr(raw_ptr, [](double* p) {
    // /* do nothing */
    // });
    // std::string outG="./G.pkl";
    // this->save_array_to_pickle(sptr,N0*N1*N0*N1,outG);
    // std::cout<<"G saved"<<std::endl;

    /// end init G_T
    /////////////////////////////////////////////////////////////////////////////////
    ///
    this->R=arma::sp_dmat(N0*N1,N0*N1);
    for (int n0=0;n0<N0;n0++)
    {
        for (int n1=0;n1<N1;n1++)
        {
            for (int m0=n0-Nx;m0<n0+Nx+1;m0++)
            {
                for (int m1=n1-Ny;m1<n1+Ny+1;m1++)
                {
                    int flat_ind_row=double_ind_to_flat_ind(n0,n1);
                    int m0_mod=mod_direction0(m0);
                    int m1_mod=mod_direction1(m1);
                    int flat_ind_col=double_ind_to_flat_ind(m0_mod,m1_mod);
                    if (flat_ind_row==flat_ind_col)
                    {
                        continue;
                    }else
                    {
                        double down = std::pow(m0 - n0, 2.0) - (m0 - n0) * (m1 - n1) + std::pow(m1 - n1, 2.0) + m1 - n1 +
                                                1.0 / 3.0;
                        R(flat_ind_row,flat_ind_col)=1.0 / down;
                    }//end if else
                }//end m1
            }//end m0
        }//end n1
    }//end n0
    this->R_T=R.t();
    //save and check
    // arma::dmat R_dense(R_T);
    // double* raw_ptr = R_dense.memptr();
    // std::shared_ptr<double[]> sptr(raw_ptr, [](double* p) {
    // /* do nothing */
    // });
    // std::string outR="./R.pkl";
    // this->save_array_to_pickle(sptr,N0*N1*N0*N1,outR);
    // std::cout<<"R saved"<<std::endl;
    ///end init R
    /////////////////////////////////////////////////////////////////////////////////
    ///init Gamma
    this->Gamma=arma::sp_dmat(N0*N1,N0*N1);
    for (int n0=0;n0<N0;n0++)
    {
        for (int n1=0;n1<N1;n1++)
        {
            for (int m0=n0-Nx;m0<n0+Nx+1;m0++)
            {
                for (int m1=n1-Ny;m1<n1+Ny+1;m1++)
                {
                    int flat_ind_row=double_ind_to_flat_ind(n0,n1);
                    int m0_mod=mod_direction0(m0);
                    int m1_mod=mod_direction1(m1);
                    int flat_ind_col=double_ind_to_flat_ind(m0_mod,m1_mod);
                    if (flat_ind_row==flat_ind_col)
                    {
                        continue;
                    }else
                    {
                        double up = std::pow(m0 - n0 - 0.5 * m1 + 0.5 * n1, 2.0);
                        double down_tmp = std::pow(m0 - n0, 2.0) - (m0 - n0) * (m1 - n1) + std::pow(m1 - n1, 2.0) + m1 - n1
                            + 1.0 / 3.0;
                        double down = std::pow(down_tmp, 2.0);
                        this->Gamma(flat_ind_row, flat_ind_col) = up / down;
                    }//end if else
                }//end m1
            }//end m0
        }//end n1
    }//end n0
    this->Gamma_T=Gamma.t();
    // arma::dmat Gamma_dense(Gamma);
    // double* raw_ptr = Gamma_dense.memptr();
    // std::shared_ptr<double[]> sptr(raw_ptr, [](double* p) {
    // /* do nothing */
    // });
    // std::string outGamma="./Gamma.pkl";
    // this->save_array_to_pickle(sptr,N0*N1*N0*N1,outGamma);
    // std::cout<<"Gamma saved"<<std::endl;
    ///end init Gamma
    ///////////////////////////////////////////////////////////////////////////////////
    ///init Theta
    this->Theta=arma::sp_dmat(N0*N1,N0*N1);
    for (int n0=0;n0<N0;n0++)
    {
        for (int n1=0;n1<N1;n1++)
        {
            for (int m0=n0-Nx;m0<n0+Nx+1;m0++)
            {
                for (int m1=n1-Ny;m1<n1+Ny+1;m1++)
                {
                    int flat_ind_row=double_ind_to_flat_ind(n0,n1);
                    int m0_mod=mod_direction0(m0);
                    int m1_mod=mod_direction1(m1);
                    int flat_ind_col=double_ind_to_flat_ind(m0_mod,m1_mod);
                    if (flat_ind_row==flat_ind_col)
                    {
                        continue;
                    }else
                    {
                        double up = (m0 - n0 - 0.5 * m1 + 0.5 * n1) * (std::sqrt(3.0) / 2.0 * m1 - std::sqrt(3.0) / 2.0 * n1
                        + std::sqrt(3.0) / 2.0);

                        double down_tmp = std::pow(m0 - n0, 2.0) - (m0 - n0) * (m1 - n1) + std::pow(m1 - n1, 2.0) + m1 - n1
                            + 1.0 / 3.0;

                        double down = std::pow(down_tmp, 2.0);
                        this->Theta(flat_ind_row, flat_ind_col) = up / down;

                    }//end if else
                }//end m1
            }//end m0
        }//end n1
    }//end n0
    this->Theta_T=Theta.t();
    // arma::dmat Theta_dense(Theta);
    // double* raw_ptr = Theta_dense.memptr();
    // std::shared_ptr<double[]> sptr(raw_ptr, [](double* p) {
    // /* do nothing */
    // });
    // std::string outTheta="./Theta.pkl";
    // this->save_array_to_pickle(sptr,N0*N1*N0*N1,outTheta);
    // std::cout<<"Theta saved"<<std::endl;
    ///end init Theta
    ///////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////
    /// init Lambda
    this->Lambda=arma::sp_dmat(N0*N1,N0*N1);
    for (int n0=0;n0<N0;n0++)
    {
        for (int n1=0;n1<N1;n1++)
        {
            for (int m0=n0-Nx;m0<n0+Nx+1;m0++)
            {
                for (int m1=n1-Ny;m1<n1+Ny+1;m1++)
                {

                    int flat_ind_row=double_ind_to_flat_ind(n0,n1);
                    int m0_mod=mod_direction0(m0);
                    int m1_mod=mod_direction1(m1);
                    int flat_ind_col=double_ind_to_flat_ind(m0_mod,m1_mod);
                    if (flat_ind_row==flat_ind_col)
                    {
                        continue;
                    }else
                    {
                        double up = std::pow(std::sqrt(3.0) / 2.0 * m1 - std::sqrt(3.0) / 2.0 * n1 + std::sqrt(3.0) / 3.0,
                                         2.0);

                        double down_tmp = std::pow(m0 - n0, 2.0) - (m0 - n0) * (m1 - n1) + std::pow(m1 - n1, 2.0) + m1 - n1
                            + 1.0 / 3.0;
                        double down = std::pow(down_tmp, 2.0);

                        this->Lambda(flat_ind_row, flat_ind_col) = up / down;

                    }//end if else
                }//end m1
            }//end m0
        }//end n1
    }//end n0
    this->Lambda_T=Lambda.t();
    // arma::dmat Lambda_dense(Lambda);
    // double* raw_ptr = Lambda_dense.memptr();
    // std::shared_ptr<double[]> sptr(raw_ptr, [](double* p) {
    // /* do nothing */
    // });
    // std::string outLambda="./Lambda.pkl";
    // this->save_array_to_pickle(sptr,N0*N1*N0*N1,outLambda);
    // std::cout<<"Lambda saved"<<std::endl;

    /// end init Lambda
    ///////////////////////////////////////////////////////////////////////////////////
}

///
/// @param x proposed value
/// @param y current value
/// @param a left end of interval
/// @param b right end of interval
/// @param epsilon half length
/// @return proposal probability S(x|y)
double mc_computation::S_uni(const double& x, const double& y, const double& a, const double& b, const double& epsilon)
{
    if (a < y and y < a + epsilon)
    {
        return 1.0 / (y - a + epsilon);
    }
    else if (a + epsilon <= y and y < b - epsilon)
    {
        return 1.0 / (2.0 * epsilon);
    }
    else if (b - epsilon <= y and y < b)
    {
        return 1.0 / (b - y + epsilon);
    }
    else
    {
        std::cerr << "value out of range." << std::endl;
        std::exit(10);
    }
}

///
/// @param x
/// @param leftEnd
/// @param rightEnd
/// @param eps
/// @return return a value within distance eps from x, on the open interval (leftEnd, rightEnd)
double mc_computation::generate_uni_open_interval(const double& x, const double& leftEnd, const double& rightEnd,
                                                  const double& eps)
{
    double xMinusEps = x - eps;
    double xPlusEps = x + eps;

    double unif_left_end = xMinusEps < leftEnd ? leftEnd : xMinusEps;
    double unif_right_end = xPlusEps > rightEnd ? rightEnd : xPlusEps;

    //    std::random_device rd;
    //    std::ranlux24_base e2(rd());

    double unif_left_end_double_on_the_right = std::nextafter(unif_left_end, std::numeric_limits<double>::infinity());


    std::uniform_real_distribution<> distUnif(unif_left_end_double_on_the_right, unif_right_end);
    //(unif_left_end_double_on_the_right, unif_right_end)

    double xNext = distUnif(e2);
    return xNext;
}
void mc_computation::proposal_uni(const arma::dvec& arma_vec_curr, arma::dvec& arma_vec_next,
                                  const int& flattened_ind)
{
    double dp_val_new = this->generate_uni_open_interval(arma_vec_curr(flattened_ind), dipole_lower_bound,
                                                         dipole_upper_bound, h);
    arma_vec_next = arma_vec_curr;
    arma_vec_next(flattened_ind) = dp_val_new;


}

/// @param Px_arma_vec Px
/// @param Py_arma_vec Py
/// @return self energy H1
double mc_computation::H1(const int& flattened_ind, const arma::dvec& Px_arma_vec, const arma::dvec& Py_arma_vec)
{
    // int flat_ind = double_ind_to_flat_ind(n0, n1);

    double px_n0n1 = Px_arma_vec(flattened_ind);

    double py_n0n1 = Py_arma_vec(flattened_ind);


    double squared_px_n0n1 = std::pow(px_n0n1, 2.0);
    double squared_py_n0n1 = std::pow(py_n0n1, 2.0);

    double part1 = alpha1 * px_n0n1 * (squared_px_n0n1 - 3.0 * squared_py_n0n1);

    double part2 = alpha2 * py_n0n1 * (3.0 * squared_px_n0n1 - squared_py_n0n1);

    double part3 = alpha3 * (
        squared_px_n0n1 * std::pow(squared_px_n0n1 - 3.0 * squared_py_n0n1, 2.0)
        - squared_py_n0n1 * std::pow(3.0 * squared_px_n0n1 - squared_py_n0n1, 2.0)
    );

    double part4 = alpha4 * px_n0n1 * py_n0n1 * (squared_px_n0n1 - 3.0 * squared_py_n0n1)
        * (3.0 * squared_px_n0n1 - squared_py_n0n1);

    double part5 = alpha5 * (squared_px_n0n1 + squared_py_n0n1);

    double part6 = alpha6 * std::pow(squared_px_n0n1 + squared_py_n0n1, 2.0);

    double part7 = alpha7 * std::pow(squared_px_n0n1 + squared_py_n0n1, 3.0);

    return part1 + part2 + part3 + part4 + part5 + part6 + part7;
}


/// @param Qx_arma_vec Qx
/// @param Qy_arma_vec Qy
/// @return self energy H2
double mc_computation::H2(const int& flattened_ind, const arma::dvec& Qx_arma_vec, const arma::dvec& Qy_arma_vec)
{
    // int flat_ind = double_ind_to_flat_ind(n0, n1);

    double qx_n0n1 = Qx_arma_vec(flattened_ind);

    double qy_n0n1 = Qy_arma_vec(flattened_ind);

    double squared_qx_n0n1 = std::pow(qx_n0n1, 2.0);

    double squared_qy_n0n1 = std::pow(qy_n0n1, 2.0);

    double part1 = alpha1 * qx_n0n1 * (squared_qx_n0n1 - 3.0 * squared_qy_n0n1);

    double part2 = alpha2 * qy_n0n1 * (3.0 * squared_qx_n0n1 - squared_qy_n0n1);

    double part3 = alpha3 * (
        squared_qx_n0n1 * std::pow(squared_qx_n0n1 - 3.0 * squared_qy_n0n1, 2.0)
        - squared_qy_n0n1 * std::pow(3.0 * squared_qx_n0n1 - squared_qy_n0n1, 2.0)
    );

    double part4 = alpha4 * qx_n0n1 * qy_n0n1 * (squared_qx_n0n1 - 3.0 * squared_qy_n0n1)
        * (3.0 * squared_qx_n0n1 - squared_qy_n0n1);

    double part5 = alpha5 * (squared_qx_n0n1 + squared_qy_n0n1);

    double part6 = alpha6 * std::pow(squared_qx_n0n1 + squared_qy_n0n1, 2.0);

    double part7 = alpha7 * std::pow(squared_qx_n0n1 + squared_qy_n0n1, 3.0);

    return part1 + part2 + part3 + part4 + part5 + part6 + part7;
}


double mc_computation::acceptanceRatio_uni(const arma::dvec& arma_vec_curr,
                                           const arma::dvec& arma_vec_next, const int& flattened_ind,
                                           const double& UCurr, const double& UNext)
{
    double numerator = -this->beta * UNext;
    double denominator = -this->beta * UCurr;
    double R = std::exp(numerator - denominator);

    double S_curr_next = S_uni(arma_vec_curr(flattened_ind), arma_vec_next(flattened_ind),
                               dipole_lower_bound, dipole_upper_bound, h);

    double S_next_curr = S_uni(arma_vec_next(flattened_ind), arma_vec_curr(flattened_ind),
                               dipole_lower_bound, dipole_upper_bound, h);

    double ratio = S_curr_next / S_next_curr;

    if (std::fetestexcept(FE_DIVBYZERO))
    {
        std::cout << "Division by zero exception caught." << std::endl;
        std::exit(15);
    }
    if (std::isnan(ratio))
    {
        std::cout << "The result is NaN." << std::endl;
        std::exit(15);
    }
    R *= ratio;

    return std::min(1.0, R);
}
void mc_computation::HPx_update_colForm(const int& flattened_ind, const arma::dvec& Px_arma_vec_curr,
                    const arma::dvec& Px_arma_vec_next,
                    const arma::dvec& Py_arma_vec_curr,
                    const arma::dvec& Qx_arma_vec_curr,
                    const arma::dvec& Qy_arma_vec_curr,
                    double& UCurr, double& UNext)
{

    double H1_self_curr = this->H1(flattened_ind, Px_arma_vec_curr, Py_arma_vec_curr);
    double H1_self_next = this->H1(flattened_ind, Px_arma_vec_next, Py_arma_vec_curr);


    double left_factor1=J_over_a_squared*arma::dot(A_T.col(flattened_ind),Px_arma_vec_curr);
    // std::cout<<"left_factor1="<<left_factor1<<std::endl;
    double left_factor2=-2.0*J_over_a_squared*arma::dot(B_T.col(flattened_ind),Px_arma_vec_curr);

    // std::cout<<"left_factor2="<<left_factor2<<std::endl;

    double left_factor3=-std::sqrt(3.0) * J_over_a_squared*arma::dot(C_T.col(flattened_ind),Py_arma_vec_curr);


    // std::cout<<"left_factor3="<<left_factor3<<std::endl;

    double left_factor4=J_over_a_squared*arma::dot(R_T.col(flattened_ind),Qx_arma_vec_curr);

    // std::cout<<"left_factor4="<<left_factor4<<std::endl;

    double left_factor5=-2.0 * J_over_a_squared * arma::dot(Gamma_T.col(flattened_ind),Qx_arma_vec_curr);



    // std::cout<<"left_factor5="<<left_factor5<<std::endl;

    double left_factor6 = -2.0 * J_over_a_squared *arma::dot(Theta_T.col(flattened_ind),Qy_arma_vec_curr);

    // std::cout<<"left_factor6="<<left_factor6<<std::endl;

    double left_factor=left_factor1+left_factor2+left_factor3\
                    + left_factor4+left_factor5+left_factor6;

    double E_int_curr = Px_arma_vec_curr(flattened_ind) *left_factor;

    double E_int_next = Px_arma_vec_next(flattened_ind) *left_factor;

    UCurr = H1_self_curr + E_int_curr;

    UNext = H1_self_next + E_int_next;
    // std::cout<<"UCurr="<<UCurr<<std::endl;
    // std::cout<<"UNext="<<UNext<<std::endl;



}


///
/// @param flattened_ind
/// @param Py_arma_vec_curr
/// @param Py_arma_vec_next
/// @param Px_arma_vec_curr
/// @param Qx_arma_vec_curr
/// @param Qy_arma_vec_curr
/// @param UCurr
/// @param UNext
void mc_computation::HPy_update_colForm(const int& flattened_ind,
                const arma::dvec& Py_arma_vec_curr, const arma::dvec& Py_arma_vec_next,
                const arma::dvec& Px_arma_vec_curr, const arma::dvec& Qx_arma_vec_curr,
                const arma::dvec& Qy_arma_vec_curr,
                double& UCurr, double& UNext)
{
    double H1_self_curr = this->H1(flattened_ind, Px_arma_vec_curr, Py_arma_vec_curr);

    double H1_self_next = this->H1(flattened_ind, Px_arma_vec_curr, Py_arma_vec_next);

    double left_factor1=J_over_a_squared*arma::dot(A_T.col(flattened_ind),Py_arma_vec_curr);

// std::cout<<"left_factor1="<<left_factor1<<std::endl;

    double left_factor2=-std::sqrt(3.0) * J_over_a_squared * arma::dot(C_T.col(flattened_ind),Px_arma_vec_curr);
    // std::cout<<"left_factor2="<<left_factor2<<std::endl;


    double left_factor3=-3.0 / 2.0 * J_over_a_squared * arma::dot(G_T.col(flattened_ind),Py_arma_vec_curr);

    // std::cout<<"left_factor3="<<left_factor3<<std::endl;

    double left_factor4=J_over_a_squared * arma::dot(R_T.col(flattened_ind),Qy_arma_vec_curr);


    // std::cout<<"left_factor4="<<left_factor4<<std::endl;

    double left_factor5=-2.0 * J_over_a_squared * arma::dot(Theta_T.col(flattened_ind),Qx_arma_vec_curr);

    // std::cout<<"left_factor5="<<left_factor5<<std::endl;

    double left_factor6=-2.0 * J_over_a_squared * arma::dot(Lambda_T.col(flattened_ind),Qy_arma_vec_curr);

    // std::cout<<"left_factor6="<<left_factor6<<std::endl;

    double left_factor=left_factor1+left_factor2+left_factor3\
                    + left_factor4+left_factor5+left_factor6;

    double E_int_curr = Py_arma_vec_curr(flattened_ind) *left_factor;

    double E_int_next = Py_arma_vec_next(flattened_ind) *left_factor;

    UCurr = H1_self_curr + E_int_curr;

    UNext = H1_self_next + E_int_next;
    // std::cout<<"UCurr="<<UCurr<<std::endl;

    // std::cout<<"UNext="<<UNext<<std::endl;

}

void mc_computation::HQx_update_colForm(const int& flattened_ind,
                    const arma::dvec& Qx_arma_vec_curr, const arma::dvec& Qx_arma_vec_next,
                    const arma::dvec& Px_arma_vec_curr,
                    const arma::dvec& Py_arma_vec_curr,
                    const arma::dvec& Qy_arma_vec_curr,
                    double& UCurr, double& UNext)
{

    double H2_self_curr = this->H2(flattened_ind, Qx_arma_vec_curr, Qy_arma_vec_curr);
    double H2_self_next = this->H2(flattened_ind, Qx_arma_vec_next, Qy_arma_vec_curr);

double left_factor1= J_over_a_squared * arma::dot(R.col(flattened_ind),Px_arma_vec_curr);
    // std::cout<<"left_factor1="<<left_factor1<<std::endl;

    double left_factor2=-2.0 * J_over_a_squared * arma::dot(Gamma.col(flattened_ind),Px_arma_vec_curr);
    // std::cout<<"left_factor2="<<left_factor2<<std::endl;

    double left_factor3=-2.0 * J_over_a_squared * arma::dot(Theta.col(flattened_ind),Py_arma_vec_curr);

    // std::cout<<"left_factor3="<<left_factor3<<std::endl;

    double left_factor4=J_over_a_squared * arma::dot(A_T.col(flattened_ind),Qx_arma_vec_curr);

    // std::cout<<"left_factor4="<<left_factor4<<std::endl;

    double left_factor5=-2.0 * J_over_a_squared * arma::dot(B_T.col(flattened_ind),Qx_arma_vec_curr);

    // std::cout<<"left_factor5="<<left_factor5<<std::endl;

    double left_factor6=-std::sqrt(3.0) * J_over_a_squared*arma::dot(C_T.col(flattened_ind),Qy_arma_vec_curr);

    // std::cout<<"left_factor6="<<left_factor6<<std::endl;

    double left_factor=left_factor1+left_factor2+left_factor3\
                        +left_factor4+left_factor5+left_factor6;
    double E_int_curr = Qx_arma_vec_curr(flattened_ind) *left_factor;
    double E_int_next = Qx_arma_vec_next(flattened_ind) *left_factor;

     UCurr = H2_self_curr + E_int_curr;

    UNext = H2_self_next + E_int_next;


    // std::cout<<"UCurr="<<UCurr<<std::endl;
// std::cout<<"UNext="<<UNext<<std::endl;


}

void mc_computation::HQy_update_colForm(const int& flattened_ind,
                    const arma::dvec& Qy_arma_vec_curr, const arma::dvec& Qy_arma_vec_next,
                    const arma::dvec& Px_arma_vec_curr,
                    const arma::dvec& Py_arma_vec_curr,
                    const arma::dvec& Qx_arma_vec_curr,
                    double& UCurr, double& UNext)
{
    double H2_self_curr = this->H2(flattened_ind, Qx_arma_vec_curr, Qy_arma_vec_curr);

    double H2_self_next = this->H2(flattened_ind, Qx_arma_vec_curr, Qy_arma_vec_next);


    double left_factor1=J_over_a_squared * arma::dot(R.col(flattened_ind),Py_arma_vec_curr);

    // std::cout<<"left_factor1="<<left_factor1<<std::endl;

    double left_factor2=-2.0 * J_over_a_squared * arma::dot(Theta.col(flattened_ind),Px_arma_vec_curr);

    // std::cout<<"left_factor2="<<left_factor2<<std::endl;

    double left_factor3=-2.0 * J_over_a_squared * arma::dot(Lambda.col(flattened_ind),Py_arma_vec_curr);

    // std::cout<<"left_factor3="<<left_factor3<<std::endl;


    double left_factor4=J_over_a_squared * arma::dot(A_T.col(flattened_ind),Qy_arma_vec_curr);

    // std::cout<<"left_factor4="<<left_factor4<<std::endl;

    double left_factor5=-std::sqrt(3.0) * J_over_a_squared * arma::dot(C_T.col(flattened_ind),Qx_arma_vec_curr);

    // std::cout<<"left_factor5="<<left_factor5<<std::endl;

    double left_factor6=-3.0 / 2.0 * J_over_a_squared * arma::dot(G_T.col(flattened_ind),Qy_arma_vec_curr);

    // std::cout<<"left_factor6="<<left_factor6<<std::endl;

    double left_factor=left_factor1+left_factor2+left_factor3\
                    +left_factor4+left_factor5+left_factor6;
    double E_int_curr = Qy_arma_vec_curr(flattened_ind) *left_factor;

    double E_int_next = Qy_arma_vec_next(flattened_ind) *left_factor;
    UCurr = H2_self_curr + E_int_curr;

    UNext = H2_self_next + E_int_next;
    // std::cout<<"UCurr="<<UCurr<<std::endl;
    // std::cout<<"UNext="<<UNext<<std::endl;












}


void mc_computation::execute_mc_one_sweep(arma::dvec& Px_arma_vec_curr,
                              arma::dvec& Py_arma_vec_curr,
                              arma::dvec& Qx_arma_vec_curr,
                              arma::dvec& Qy_arma_vec_curr,
                              double& UCurr,
                              arma::dvec& Px_arma_vec_next,
                              arma::dvec& Py_arma_vec_next,
                              arma::dvec& Qx_arma_vec_next,
                              arma::dvec& Qy_arma_vec_next)
{

    double UNext = 0;
    //update Px
    for (int i = 0; i < N0 * N1; i++)
    {
        //end updating Px
        int flattened_ind = unif_in_0_N0N1(e2);
        this->proposal_uni(Px_arma_vec_curr, Px_arma_vec_next, flattened_ind);

        this->HPx_update_colForm(flattened_ind, Px_arma_vec_curr, Px_arma_vec_next,
                         Py_arma_vec_curr, Qx_arma_vec_curr, Qy_arma_vec_curr, UCurr, UNext);

        double r = this->acceptanceRatio_uni(Px_arma_vec_curr, Px_arma_vec_next,
                                             flattened_ind, UCurr, UNext);


        double u = distUnif01(e2);

        if (u <= r)
        {
            Px_arma_vec_curr = Px_arma_vec_next;
            UCurr = UNext;
        } //end of accept-reject
    }//end updating Px

    //update Py
    for (int i = 0; i < N0 * N1; i++)
    {int flattened_ind = unif_in_0_N0N1(e2);
        this->proposal_uni(Py_arma_vec_curr, Py_arma_vec_next, flattened_ind);
        this->HPy_update_colForm(flattened_ind, Py_arma_vec_curr, Py_arma_vec_next,
                         Px_arma_vec_curr, Qx_arma_vec_curr, Qy_arma_vec_curr, UCurr, UNext);

        double r = this->acceptanceRatio_uni(Py_arma_vec_curr, Py_arma_vec_next, flattened_ind, UCurr, UNext);
        double u = distUnif01(e2);
        if (u <= r)
        {
            Py_arma_vec_curr = Py_arma_vec_next;
            UCurr = UNext;
        } //end of accept-reject
    }//end updating Py

    //update Qx
    for (int i = 0; i < N0 * N1; i++)
    {
        int flattened_ind = unif_in_0_N0N1(e2);
        this->proposal_uni(Qx_arma_vec_curr, Qx_arma_vec_next, flattened_ind);
        this->HQx_update_colForm(flattened_ind, Qx_arma_vec_curr, Qx_arma_vec_next,
                         Px_arma_vec_curr, Py_arma_vec_curr,
                         Qy_arma_vec_curr,
                         UCurr, UNext);
        double r = this->acceptanceRatio_uni(Qx_arma_vec_curr, Qx_arma_vec_next, flattened_ind, UCurr, UNext);
        double u = distUnif01(e2);
        if (u <= r)
        {
            Qx_arma_vec_curr = Qx_arma_vec_next;
            UCurr = UNext;
        } //end of accept-reject
    }//end updating Qx

    //update Qy
    for (int i = 0; i < N0 * N1; i++)
    {
        int flattened_ind = unif_in_0_N0N1(e2);
        this->proposal_uni(Qy_arma_vec_curr, Qy_arma_vec_next, flattened_ind);
        this->HQy_update_colForm(flattened_ind, Qy_arma_vec_curr, Qy_arma_vec_next,
                         Px_arma_vec_curr,
                         Py_arma_vec_curr,
                         Qx_arma_vec_curr,
                         UCurr, UNext);

        double r=this->acceptanceRatio_uni(Qy_arma_vec_curr,Qy_arma_vec_next,flattened_ind,UCurr,
            UNext);
        double u = distUnif01(e2);

        if (u <= r)
        {
            Qy_arma_vec_curr=Qy_arma_vec_next;
            UCurr = UNext;
        }//end of accept-reject


    }//end updating Qy

}

void mc_computation::init_and_run()
{
    this->init_mats();

    this->init_Px_Py_Qx_Qy();
    // int flattened_ind=47;
    // arma::dvec Px_arma_vec_curr = arma::randu<arma::dvec>(N0*N1);
    // arma::dvec Px_arma_vec_next = arma::randu<arma::dvec>(N0*N1);
    // arma::dvec Py_arma_vec_curr=arma::randu<arma::dvec>(N0*N1);
    // arma::dvec Qx_arma_vec_curr=arma::randu<arma::dvec>(N0*N1);
    // arma::dvec Qy_arma_vec_curr=arma::randu<arma::dvec>(N0*N1);
    // double UCurr,UNext;
    // this->HQy_update_colForm(flattened_ind,Px_arma_vec_curr,Px_arma_vec_next,
    //     Py_arma_vec_curr,Qx_arma_vec_curr,
    //     Qy_arma_vec_curr,UCurr,UNext);

}