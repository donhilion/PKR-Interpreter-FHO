__author__ = 'Donhilion'

factorial = """
prog
    let
        fac=fun
                a
            =>
                if
                    a>0
                then
                    a*call fac(a-1)
                else
                    1
                fi
            end
    in
        call fac(4)
end
"""

fibonacci = """
prog
    let
        f=fun
                a
            =>
                if
                    a>1
                then
                    call f(a-1) + call f(a-2)
                else
                    1
                fi
            end
    in
        call f(5)
end
"""

square = """
prog
    let
        square=fun
            z
            =>
                z*z
            end
    in
        call square(4)
end
"""

exp = """
prog
    let
        exp=fun
            a, b
            =>
                call expRek(a,b,1)
            end;
        expRek=fun
            a, b, erg
            =>
                if
                    b < 1
                then
                    erg
                else
                    call expRek(a,b-1,erg*a)
                fi
            end
    in
        call exp(2,10)
end
"""