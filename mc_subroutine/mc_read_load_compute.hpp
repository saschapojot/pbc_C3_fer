//
// Created by adada on 20/3/2025.
//

#ifndef MC_READ_LOAD_COMPUTE_HPP
#define MC_READ_LOAD_COMPUTE_HPP
#include <armadillo>
#include <boost/filesystem.hpp>
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
#include <cfenv> // for floating-point exceptions
#include <fstream>
#include <Python.h>
#include <random>
#include <sstream>
#include <string>
#include <vector>
#endif //MC_READ_LOAD_COMPUTE_HPP


namespace fs = boost::filesystem;
namespace py = boost::python;
namespace np = boost::python::numpy;

class mc_computation
{




public:
    double T; // temperature
    double beta;
    double a;
    double a_squared;
    double J;
    double J_over_a_squared;

    double h; // step size
    int sweepToWrite;
    int newFlushNum;
    int flushLastFile;
    std::string TDirRoot;
    std::string U_dipole_dataDir;
    std::ranlux24_base e2;
    std::uniform_real_distribution<> distUnif01;
    int sweep_multiple;
    std::string out_U_path;
    std::string out_Px_path;

    std::string out_Py_path;
    std::string out_Qx_path;
    std::string out_Qy_path;
    //data in 1 flush
    std::shared_ptr<double[]> U_data_all_ptr; //all U data
    std::shared_ptr<double[]> Px_all_ptr; //all Px data
    std::shared_ptr<double[]> Py_all_ptr; //all Py data
    std::shared_ptr<double[]> Qx_all_ptr; //all Qx data
    std::shared_ptr<double[]> Qy_all_ptr; //all Qy data

    //initial value
    std::shared_ptr<double[]> Px_init;
    std::shared_ptr<double[]> Py_init;
    std::shared_ptr<double[]> Qx_init;
    std::shared_ptr<double[]> Qy_init;

    // //for computation
    // arma::dvec Px_arma_vec;
    // arma::dvec Py_arma_vec;
    //
    // arma::dvec Qx_arma_vec;
    // arma::dvec Qy_arma_vec;

    double q;
    double alpha1, alpha2, alpha3, alpha4, alpha5, alpha6, alpha7;
    int N0, N1;
    int Nx, Ny;

    arma::dmat A, B, C, G, R, Gamma, Theta, Lambda;

    std::uniform_int_distribution<int> unif_in_0_N0N1;

    double dipole_lower_bound;
    double dipole_upper_bound;
};