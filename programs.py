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

vars = """
prog
    let
        y = 2;
        x = 1 + y
    in
        let
            y = 5
        in
            x
        end
    end
"""

stat = """
prog
    let
        y = 1;
        f = fun
            x
            =>
            x + y
            end
    in
        let
            y = 100
        in
            call f(5)
        end
    end
"""

high = """
prog
    let
        y = 1;
        f = fun
            x
            =>
                fun z =>
                    x + y + z
                end
            end
    in
        let
            y = 100;
            m = call f(5)
        in
            call m(2)
        end
    end
"""