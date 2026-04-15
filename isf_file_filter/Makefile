
#
PROGNAME= isf_file_filter
ALLSOURCECODE=  \
   $(PROGNAME).f  
#
#
SOURCES= \
        $(ALLSOURCECODE)
#
OPTIM=	  -O3
TOPDIR=   ~/NGI/T/Tsunami/Seismic/arrivals/isf_file_filter
OS= $(shell uname)
BINDIR=  .
EXEFILE= $(BINDIR)/$(PROGNAME)
FORTRAN= gfortran
#
LIBS=    
#
backup:
	cp -ip $(ALLSOURCECODE) ./BACKUP ; \
	cd ./BACKUP ; \
	\rm -f *.gz ; \
	gzip $(ALLSOURCECODE) ; \
	cd ../
#
$(PROGNAME):	$(ALLSOURCECODE) $(LIBS)
	$(FORTRAN) -o $(EXEFILE) $(ALLSOURCECODE) $(LIBS) $(OPTIM)
