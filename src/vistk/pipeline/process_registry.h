/*ckwg +5
 * Copyright 2011 by Kitware, Inc. All Rights Reserved. Please refer to
 * KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
 * Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.
 */

#ifndef VISTK_PIPELINE_PROCESS_REGISTRY_H
#define VISTK_PIPELINE_PROCESS_REGISTRY_H

#include "pipeline-config.h"

#include "types.h"

#include <boost/function.hpp>
#include <boost/scoped_ptr.hpp>

#include <string>
#include <vector>

/**
 * \file process_registry.h
 *
 * \brief Header for the \link vistk::process_registry process registry\endlink.
 */

namespace vistk
{

/// A function which returns a \ref process.
typedef boost::function<process_t (config_t const& config)> process_ctor_t;

/**
 * \class process_registry process_registry.h <vistk/pipeline/process_registry.h>
 *
 * \brief A registry of processes which can generate processes of a different types.
 *
 * \ingroup registries
 */
class VISTK_PIPELINE_EXPORT process_registry
{
  public:
    /// The type of registry keys.
    typedef std::string type_t;
    /// The type for a description of the pipeline.
    typedef std::string description_t;
    /// A group of types.
    typedef std::vector<type_t> types_t;
    /// The type of a module name.
    typedef std::string module_t;

    /**
     * \brief Destructor.
     */
    ~process_registry();

    /**
     * \brief Adds a process type to the registry.
     *
     * \throws null_process_ctor_exception Thrown if \p ctor is \c NULL.
     * \throws process_type_already_exists_exception Thrown if the type already exists.
     *
     * \param type The name of the \ref process type.
     * \param desc A description of the type.
     * \param ctor The function which creates the process of the \p type.
     */
    void register_process(type_t const& type, description_t const& desc, process_ctor_t ctor);
    /**
     * \brief Creates process of a specific type.
     *
     * \throws no_such_process_type_exception Thrown if the type is not known.
     *
     * \param type The name of the type of \ref process to create.
     * \param config The configuration to pass the \ref process.
     *
     * \returns A new process of type \p type.
     */
    process_t create_process(type_t const& type, config_t const& config) const;

    /**
     * \brief Query for all available types.
     *
     * \returns All available types in the registry.
     */
    types_t types() const;
    /**
     * \brief Query for a description of a type.
     *
     * \param type The name of the type to description.
     *
     * \returns The description for the type \p type.
     */
    description_t description(type_t const& type) const;

    /**
     * \brief Marks a module as loaded.
     *
     * \param module The module to mark as loaded.
     */
    void mark_module_as_loaded(module_t const& module);
    /**
     * \brief Queries if a module has already been loaded.
     *
     * \param module The module to query.
     *
     * \returns True if the module has already been loaded, false otherwise.
     */
    bool is_module_loaded(module_t const& module) const;

    /**
     * \brief Accessor to the registry.
     *
     * \returns The instance of the registry to use.
     */
    static process_registry_t self();
  private:
    process_registry();

    class priv;
    boost::scoped_ptr<priv> d;
};

}

/**
 * \def CREATE_PROCESS
 *
 * \brief A macro to create a process.
 *
 * This is to help reduce the amount of code needed in registration functions.
 *
 * \param cls The process to create.
 */
#define CREATE_PROCESS(cls) \
  &boost::make_shared<cls, config_t const&>

#endif // VISTK_PIPELINE_PROCESS_REGISTRY_H
