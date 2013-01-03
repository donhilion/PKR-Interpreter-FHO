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
