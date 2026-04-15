C
C isf_file_filter
C reads in strings of length 240
C
CIR        GERES  82.83 329.0 P        2011/03/11 12:08:57.2     0.3  44.1         5.9       T__   8.9       8.5  0.80  __ mb     4.9   602227442             258991047 ISC   IR                      ??? ???    48.8451   13.7016  1137.0    0.0
CIR        GERES  82.83 329.0 P        2011/03/11 12:08
      PROGRAM isf_file_filter
      IMPLICIT NONE
C
      CHARACTER *(240) CHLINE
      CHARACTER *(23)  CHTIME
C     yyyy-mm-ddThh:mm:ss.sss
      REAL*4           AZI
      REAL*4           SLOW
      REAL*4           SNR
C
 50   CONTINUE
      CHLINE = ' '
      READ (5,'(A)',ERR=99, END=60 ) CHLINE
      IF ( CHLINE(1:2).NE.'IR' ) GOTO 50
      READ ( CHLINE( 69: 73), *, END=50, ERR=50) AZI
      READ ( CHLINE( 82: 85), *, END=50, ERR=50) SLOW
      READ ( CHLINE( 97:101), *, END=50, ERR=50) SNR
      CHTIME        = ' '
      CHTIME( 1: 4) = CHLINE( 39: 42)
      CHTIME( 5: 5) = '-'
      CHTIME( 6: 7) = CHLINE( 44: 45)
      CHTIME( 8: 8) = '-'
      CHTIME( 9:10) = CHLINE( 47: 48)
      CHTIME(11:11) = 'T'
      CHTIME(12:23) = CHLINE( 50: 61)
      IF ( CHTIME(23:23).EQ.' ' )  CHTIME(23:23) = '0'
      IF ( CHTIME(22:22).EQ.' ' )  CHTIME(22:22) = '0'
      IF ( CHTIME(21:21).EQ.' ' )  CHTIME(21:21) = '0'
c     WRITE (6,'(A)')  CHLINE
      WRITE (6,'(240A)') 
     1                CHLINE( 11: 15), ' ',
     3                CHLINE( 17: 22), ' ', 
     2                CHLINE( 24: 28), ' ',
     2                CHLINE( 30: 37), ' ',
     X                CHTIME( 1:23), ' ',
     X                CHLINE( 69: 73), ' ',
     X                CHLINE( 82: 85), ' ',
     X                CHLINE( 98:101), ' ',
     X                CHLINE(135:144), ' ',
     X                CHLINE(157:166), ' ', CHLINE(208:225)
      GOTO 50
 60   CONTINUE
      CALL EXIT(0)
 99   CONTINUE
      WRITE (6,*) 'Error with line ', CHLINE
      CALL EXIT(1)
      END
