ARCH       := $(shell getconf LONG_BIT)
OS         := $(shell cat /etc/issue)

ifneq (,$(wildcard /etc/redhat-release))
    RHEL_OS := $(shell cat /etc/redhat-release)
endif

# Gets Driver Branch
DRIVER_BRANCH := $(shell nvidia-smi | grep Driver | cut -f 3 -d' ' | cut -f 1 -d '.')

# Location of the CUDA Toolkit
CUDA_PATH ?= "/usr/local/cuda-8.0"

ifeq (${ARCH},$(filter ${ARCH},32 64))
    # If correct architecture and libnvidia-ml library is not found 
    # within the environment, build using the stub library
    
    ifneq (,$(findstring Ubuntu,$(OS)))
        DEB := $(shell dpkg -l | grep cuda)
        ifneq (,$(findstring cuda, $(DEB)))
            NVML_LIB := /usr/lib/nvidia-$(DRIVER_BRANCH)
        else 
            NVML_LIB := /lib${ARCH}
        endif
    endif

    ifneq (,$(findstring SUSE,$(OS)))
        RPM := $(shell rpm -qa cuda*)
        ifneq (,$(findstring cuda, $(RPM)))
            NVML_LIB := /usr/lib${ARCH}
        else
            NVML_LIB := /lib${ARCH}
        endif
    endif

    ifneq (,$(findstring CentOS,$(RHEL_OS)))
        RPM := $(shell rpm -qa cuda*)
        ifneq (,$(findstring cuda, $(RPM)))
            NVML_LIB := /usr/lib${ARCH}/nvidia
        else
            NVML_LIB := /lib${ARCH}
        endif
    endif

    ifneq (,$(findstring Red Hat,$(RHEL_OS)))
        RPM := $(shell rpm -qa cuda*)
        ifneq (,$(findstring cuda, $(RPM)))
            NVML_LIB := /usr/lib${ARCH}/nvidia
        else
            NVML_LIB := /lib${ARCH}
        endif
    endif

    ifneq (,$(findstring Fedora,$(RHEL_OS)))
        RPM := $(shell rpm -qa cuda*)
        ifneq (,$(findstring cuda, $(RPM)))
            NVML_LIB := /usr/lib${ARCH}/nvidia
        else
            NVML_LIB := /lib${ARCH}
        endif
    endif

else
    NVML_LIB := ../../lib${ARCH}/stubs/
    $(info "libnvidia-ml.so.1" not found, using stub library.)
endif

ifneq (${ARCH},$(filter ${ARCH},32 64))
	$(error Unknown architecture!)
endif

NVML_LIB += ../lib/
NVML_LIB_L := $(addprefix -L , $(NVML_LIB))

CFLAGS  := -I ../../include -I ../include
LDFLAGS := -lnvidia-ml $(NVML_LIB_L)

all: example supportedVgpus
example: example.o
	$(CC) $< $(CFLAGS) $(LDFLAGS) -o $@
supportedVgpus: supportedVgpus.o
	$(CC) $< $(CFLAGS) $(LDFLAGS) -o $@
clean:
	-@rm -f example.o
	-@rm -f example
	-@rm -f supportedVgpus.o
	-@rm -f supportedVgpus
